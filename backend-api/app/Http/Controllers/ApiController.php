<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\SensorLog;
use App\Models\AiDetection;

class ApiController extends Controller
{
    // 1. Endpoint untuk menerima tembakan data dari ESP32 (IoT Rigin)
    public function storeSensorData(Request $request)
    {
        $request->validate([
            'temperature' => 'required|numeric',
            'air_humidity' => 'required|numeric',
            'soil_moisture' => 'required|numeric',
            'pump_status' => 'required|boolean',
        ]);

        $log = SensorLog::create($request->all());

        return response()->json([
            'status' => 'success',
            'message' => 'Data sensor IoT berhasil disimpan!',
            'data' => $log
        ], 201);
    }

    // 2. Endpoint untuk menerima tembakan data dari Python YOLOv8 (AI Mufti)
    public function storeAiData(Request $request)
    {
        $request->validate([
            'raw_count' => 'required|integer',
            'partially_ripe_count' => 'required|integer',
            'ripe_count' => 'required|integer',
        ]);

        $ai = AiDetection::create($request->all());

        return response()->json([
            'status' => 'success',
            'message' => 'Data deteksi AI tomat berhasil disimpan!',
            'data' => $ai
        ], 201);
    }

    // 3. Endpoint untuk ditarik (GET) oleh Dashboard SolidJS lu
    public function getDashboardData()
    {
        // Ambil 1 data paling baru untuk card status di atas
        $latestSensor = SensorLog::latest()->first();
        $latestAi = AiDetection::latest()->first();
        
        // Ambil 5 data history sensor terakhir untuk tabel log di bawah
        $historyLogs = SensorLog::latest()->take(5)->get();

        return response()->json([
            'status' => 'success',
            'data' => [
                'current_sensor' => $latestSensor,
                'current_ai' => $latestAi,
                'history_logs' => $historyLogs
            ]
        ], 200);
    }
}