

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
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-np.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe.unsqueeze(0))

    def forward(self, x):
        return x + self.pe[:, :x.size(1), :]
class HeatwaveTransformer(nn.Module):
    def __init__(self, input_size=5, d_model=64, nhead=4, num_layers=3, dim_feedforward=128, dropout=0.3):
        super(HeatwaveTransformer, self).__init__()
        self.input_projection = nn.Linear(input_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model)
        encoder_layers = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, dim_feedforward=dim_feedforward,
            dropout=dropout, activation='gelu', batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layers, num_layers=num_layers)
        self.fc= nn.Sequential(
            nn.LayerNorm(d_model),
            nn.Linear(d_model, 32), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(32,1)
        )
    def forward(self, x):
        x = self.input_projection(x)
        x = self.pos_encoder(x)
        x = self.transformer_encoder(x)
        return self.fc(x[:,-1,:])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# MODEL_PATH = os.path.join(BASE_DIR, "best_geosat_tuned.pth")
# SCALER_PATH = os.path.join(BASE_DIR, "tuned_scaler.joblib")

flood_model = None
flood_scaler = None
heat_model = None
heat_scaler = None


try:
    print("loading 8-Feature Deep Learning Engine into memory")
    flood_scaler = joblib.load(os.path.join(BASE_DIR, "tuned_scaler.joblib"))
    flood_model = GeoSatTunedNet(input_size=8)
    flood_model.load_state_dict(torch.load(os.path.join(BASE_DIR, "best_geosat_tuned.pth"), map_location=torch.device('cpu'), weights_only=True))
    flood_model.eval()
    print(" flood engine online!")


    heat_scaler = joblib.load(os.path.join(BASE_DIR, "heatwave_scaler.joblib"))
    heat_model = HeatwaveTransformer(input_size=5)
    heat_model.load_state_dict(torch.load(os.path.join(BASE_DIR, "best_heatwave_transformer.pth"), map_location=torch.device('cpu'), weights_only=True))
    heat_model.eval()
    print(" heat engine online!")
except Exception as e:
    print(f"model loading failed: {str(e)}")


def predict_flood_risk(weather_history):
    if flood_model is None or flood_scaler is None:
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
    scaled_features = flood_scaler.transform(np.array(features))
    tensor_features = torch.tensor(scaled_features, dtype=torch.float32).unsqueeze(0)
    with torch.no_grad():
        logits = flood_model(tensor_features)
        probability = torch.sigmoid(logits).item()
    return probability*100.0


def predict_heatwave_risk(weather_history):
    if heat_model is None or heat_scaler is None:
        return 0.0
    
    latest_temp = weather_history[-1]['temp']
    if latest_temp >= 45.0:
        return 99.8  
    
    features = []
    for i in range(len(weather_history)):
        w = weather_history[i]
        t_3 = [h['temp'] for h in weather_history[max(0, i-2):i+1]]
        t_7 = [h['temp'] for h in weather_history[max(0, i-6):i+1]]
        features.append([w['temp'], w['humidity'], w['rainfall'], sum(t_3)/len(t_3), sum(t_7)/len(t_7)])

    try:
        scaled_features = heat_scaler.transform(np.array(features))
        tensor_features = torch.tensor(scaled_features, dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            logits = heat_model(tensor_features)
            probability = torch.sigmoid(logits).item()
        return probability * 100.0
    except:
        return min((latest_temp / 45.0) * 100, 100) if latest_temp > 35 else 10.0