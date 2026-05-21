<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ApiController;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');

// Rute POST (Menerima data dari alat)
Route::post('/sensor', [ApiController::class, 'storeSensorData']);
Route::post('/vision', [ApiController::class, 'storeAiData']);

// Rute GET (Mengirim data ke UI Solid.JS)
Route::get('/dashboard', [ApiController::class, 'getDashboardData']);