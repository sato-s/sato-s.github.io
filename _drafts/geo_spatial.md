---
layout: post
title: GPSデータの取り扱いのためのライブラリ・サービス
date: '2019-01-15T00:00:00.000+09:00'
author: s sato 
tags:
- gps
- python
- javascript
---

最近、GPSデータを扱う機会がやたらと多いのでメモ  

#### [Leaflet.js](https://leafletjs.com/)

地図描画ライブラリ、シンプルで使いやすい。

#### [Leaflet Provider Preview](https://leaflet-extras.github.io/leaflet-providers/preview/)

Leafletで使用可能なフリーのタイルレイヤー集  

#### [MapBox](https://www.mapbox.com/)

自分好みのタイルレイヤーを作れるサービス  

#### [OpenLayers](https://openlayers.org/)

地図描画ライブラリ。Leafletよりもすこしハードルが高い  
Leafletではできない。地図の回転ができる。  

#### [Proj4](https://proj4.org/)

GPS座標のプロジェクションの変換ライブラリ。  
OpenlayersやLeafletでプロジェクションを変更する際には、これの仕様を意識する必要がある。  

#### [kepler.gl](http://kepler.gl/#/)

Uber製の地図表示ライブラリ、webGLでの描画。  
かなりイケてる分析画面ができる。  

#### [Turf.js](http://turfjs.org/)

javascriptの空間データ分析ライブラリ、2つのGPSデータを結ぶ線が来たから何度傾いているか？2つの多角形の共通部分など、
複雑な空間データの計算をやってくれる。  

#### [Shapely](https://github.com/Toblerity/Shapely)

pythonの空間データ分析ライブラリ、バックエンド側で計算する際にはこっちを使う  

#### [GPSies](https://www.gpsies.com/createTrack.do?language=en)

地図上にGPSのトラックをかけるサービス  
いろいろな形式でエクスポートできるので便利  

