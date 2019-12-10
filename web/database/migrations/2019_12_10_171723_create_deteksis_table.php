<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateDeteksisTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('deteksis', function (Blueprint $table) {
            $table->bigIncrements('id');
            $table->string('nama', 25);
            $table->dateTime('waktu');
            $table->float('probabilitas');
            $table->string('gambar', 100);
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::dropIfExists('deteksis');
    }
}
