<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Final Project Visi Komputer</title>

    <!-- Style -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
    <style>
        .nganu {
            height: 25em;
            width: auto;
            overflow-y: auto;
        }

        .deteksi {
            margin-right: 0 !important;
            margin-bottom: 20px;
        }

        .jumbotron{
            position: absolute;
            top: 0;
            left: 0;
            height: 100%;
            width: 100%;
            display: table;
            margin-bottom: 0 !important;
        }

        .main-container{
            vertical-align: middle;
            display: table-cell;
        }


    </style>
</head>
<body>
    <div class="jumbotron">
        <div class="container main-container">
            <div class="row">
                <div class="col-sm-8">
                    <video class="img-fluid rounded" width="1280" height="720" autoplay loop muted controls>
                        <source src="{{ env('STREAM_URL') }}" type="video/ogg" />
                    </video>
                </div>
                <div class="col-sm-4 text-center">
                    <h3> LOG </h3>
                    <div class="nganu border border-secondary rounded">
                        @foreach ($deteksis as $deteksi)
                            <div class="row deteksi deteksi-{{ $deteksi->id }}">
                                <img class="col-md-4 img-fluid rounded gambar" src="{{ URL::asset($deteksi->gambar) }}">
                                <div class="col-md-8 data-text">
                                    <label class="row nama">Nama: {{ $deteksi->nama }}</label>
                                    <label class="row waktu">Waktu: {{ $deteksi->waktu }}</label>
                                </div>
                            </div>
                        @endforeach
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- Script -->
    <script src="https://code.jquery.com/jquery-3.4.1.slim.min.js" integrity="sha384-J6qa4849blE2+poT4WnyKhv5vZF5SrPo0iEjwBvKU7imGFAV0wwj1yYfoRSJoZ+n" crossorigin="anonymous"></script>
    <script src="https://code.jquery.com/jquery-3.4.1.min.js" integrity="sha256-CSXorXvZcTkaix6Yvo6HppcZGetbYMGWSFlBw8HfCJo=" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js" integrity="sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6" crossorigin="anonymous"></script>
    <script>
        let jsonData = new Array();
        // Melakukan update setiap 1 detik sekali
        const removeChildren = (node) => {
            while (node.firstChild) {
                node.removeChild(node.firstChild);
            }
        }

        $(document).ready(function() {
            setInterval(function() {
                $.ajax({
                    url: '{{ route('updateDeteksi') }}',
                    dataType: 'json',
                    data: {
                        "_token": "{{ csrf_token() }}",

                    },
                    success: function(response) {
                        jsonData = response;
                        console.log(jsonData);
                        let logDiv = document.querySelector('.nganu');
                        let fragment = document.createDocumentFragment();
                        for (const data of jsonData) {
                            let dataDiv = document.createElement('div');
                            dataDiv.setAttribute('class', `deteksi-${data.id} row deteksi`);

                            let image = document.createElement('img');
                            image.setAttribute('class', 'col-md-4 img-fluid rounded gambar');
                            image.setAttribute('src', `${data.gambar}`);
                            dataDiv.appendChild(image)

                            let nama = document.createElement('label');
                            nama.setAttribute('class', 'row nama');
                            nama.textContent = `Nama: ${data.nama}`;
                            let waktu = document.createElement('label');
                            waktu.setAttribute('class', 'row waktu');
                            waktu.textContent = `Waktu: ${data.waktu}`;

                            let text = document.createElement('div');
                            text.setAttribute('class', 'data-text col-md-8');
                            text.appendChild(nama);
                            text.appendChild(waktu);

                            dataDiv.appendChild(text);
                            fragment.appendChild(dataDiv);
                        }
                        removeChildren(logDiv);
                        logDiv.appendChild(fragment);
                    },
                    error: function(response) {
                        jsonData = null;
                    }
                });


            }, 5000);
        });
    </script>
</body>
</html>
