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
        Schema::create('ai_detections', function (Blueprint $table) {
            $table->id();
            $table->integer('raw_count')->default(0); // Jumlah tomat mentah (hijau)
            $table->integer('partially_ripe_count')->default(0); // Jumlah tomat mengkal (kuning/oranye)
            $table->integer('ripe_count')->default(0); // Jumlah tomat matang (merah)
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('ai_detections');
    }
};
