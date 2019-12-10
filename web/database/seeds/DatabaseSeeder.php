<?php

use Illuminate\Database\Seeder;
use Carbon\Carbon;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed the application's database.
     *
     * @return void
     */
    public function run()
    {
        // $this->call(UsersTableSeeder::class);

        for($i = 0;$i < 25; $i++) {
            DB::table('deteksis')->insert([
                'nama' => 'kunkun',
                'waktu' =>  Carbon::now(),
                'probabilitas' => 1,
                'gambar' => '/images/dummy250.png'
            ]);
        }
    }
}
