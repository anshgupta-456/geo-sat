import torch
import torch.nn as nn
import joblib
import os
import numpy as np
from datetime import datetime

class GeoSatTunedNet(nn.Module):
    def __init__(self, input_size=8, cnn_filters=64, lstm_hidden=128, num_layers=2, dropout=0.3):
        super(GeoSatTunedNet, self).__init__()
        self.conv1 = nn.Conv1d(in_channels=input_size, out_channels=cnn_filters, kernel_size=3, padding=1)
        self.relu = nn.GELU()
        self.dropout1d = nn.Dropout1d(p=dropout)

        self.lstm = nn.LSTM(
            input_size = cnn_filters,
            hidden_size=lstm_hidden,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout,
            bidirectional=True
        )

        self.fc = nn.Sequential(
            nn.Linear(lstm_hidden*2, 64), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(64,32), nn.GELU(), nn.Linear(32,1)
        )

    def forward(self, x):
        x = x.permute(0,2,1)
        x = self.conv1(x)
        x = self.relu(x)
        x = self.dropout1d(x)
        x = x.permute(0,2,1)
        out,_ = self.lstm(x)
        return self.fc(out[:,-1,:])
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "best_geosat_tuned.pth")
SCALER_PATH = os.path.join(BASE_DIR, "tuned_scaler.joblib")

model = None
scaler = None

try:
    print("loading 8-Feature Deep Learning Engine into memory")
    scaler = joblib.load(SCALER_PATH)
    model = GeoSatTunedNet(input_size=8)

    model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu'), weights_only=True))
    model.eval()
    print("model online")
except Exception as e:
    print(f"model loading failed: {str(e)}")


def predict_flood_risk(weather_history):
    if model is None or scaler is None:
        return 0.0
    features=[]
    for i in range(len(weather_history)):
        temp = weather_history[i]['temp']
        rain = weather_history[i]['rainfall']
        hum = weather_history[i]['humidity']

        rain_3d = sum([w['rainfall'] for w in weather_history[max(0, i-2):i+1]])
        rain_7d = sum([w['rainfall'] for w in weather_history[max(0, i-6):i+1]])
        rain_14d = sum([w['rainfall'] for w in weather_history[max(0, i-13):i+1]])

        month = weather_history[i]['timestamp'].month
        month_sin = np.sin(2 * np.pi * month / 12)
        month_cos = np.cos(2 * np.pi * month / 12)
        features.append([temp, rain, hum, rain_3d, rain_7d, rain_14d, month_sin, month_cos])
    scaled_features = scaler.transform(np.array(features))
    tensor_features = torch.tensor(scaled_features, dtype=torch.float32).unsqueeze(0)
    with torch.no_grad():
        logits = model(tensor_features)
        probability = torch.sigmoid(logits).item()
    return probability*100.0

