<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('sensor_logs', function (Blueprint $table) {
            $table->id();
            $table->decimal('temperature', 5, 2); // Contoh: 28.50
            $table->decimal('air_humidity', 5, 2); // Contoh: 65.00
            $table->decimal('soil_moisture', 5, 2); // Contoh: 35.00
            $table->boolean('pump_status')->default(false); // true untuk ON, false untuk OFF
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('sensor_logs');
    }
};
