<?php

namespace App\Http\Controllers;

use App\Deteksi;
use Illuminate\Http\Request;

class DeteksiController extends Controller
{
    /**
     * Display a listing of the resource.
     *
     * @return \Illuminate\Http\Response
     */
    public function index()
    {
        $deteksis = Deteksi::orderBy('waktu', 'desc')->take(10)->get();
        return view('stream', compact('deteksis'));
    }

    public function query()
    {
        $deteksis = Deteksi::orderBy('waktu', 'desc')->take(10)->get();
        return $deteksis;
    }

    /**
     * Show the form for creating a new resource.
     *
     * @return \Illuminate\Http\Response
     */
    public function create()
    {
        //
    }

    /**
     * Store a newly created resource in storage.
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\Response
     */
    public function store(Request $request)
    {
        //
    }

    /**
     * Display the specified resource.
     *
     * @param  \App\Deteksi  $deteksi
     * @return \Illuminate\Http\Response
     */
    public function show(Deteksi $deteksi)
    {
        //
    }

    /**
     * Show the form for editing the specified resource.
     *
     * @param  \App\Deteksi  $deteksi
     * @return \Illuminate\Http\Response
     */
    public function edit(Deteksi $deteksi)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  \App\Deteksi  $deteksi
     * @return \Illuminate\Http\Response
     */
    public function update(Request $request, Deteksi $deteksi)
    {
        //
    }

    /**
     * Remove the specified resource from storage.
     *
     * @param  \App\Deteksi  $deteksi
     * @return \Illuminate\Http\Response
     */
    public function destroy(Deteksi $deteksi)
    {
        //
    }
}
