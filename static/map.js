// 建立地圖
var map = L.map('map').setView([25.0330,121.5654],13);

L.tileLayer(
'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
{ attribution:'© OpenStreetMap' }
).addTo(map);


// GPS 定位
navigator.geolocation.getCurrentPosition(function(position){

    var lat = position.coords.latitude;
    var lng = position.coords.longitude;

    map.setView([lat,lng],16);

    var marker = L.marker([lat,lng]).addTo(map);

    marker.bindPopup("你目前的位置").openPopup();

});


// 讀取資料庫打卡
function loadCheckins(){

    fetch("/checkins")
    .then(response => response.json())
    .then(data => {

        data.forEach(function(c){

            var marker = L.marker([c.lat, c.lng]).addTo(map);

            var popupContent =
                "<b>打卡位置</b><br>" +
                "時間: " + c.time + "<br>";

            // 如果有照片就顯示
            if(c.photo){
                popupContent +=
                    "<img src='" + c.photo + "' width='200'>";
            }

            marker.bindPopup(popupContent);

        });

    });

}

loadCheckins();