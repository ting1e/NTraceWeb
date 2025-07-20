// /static/map.js

let map;
let latlngs = [];
let polyline;
let markersGroup;

/**
 * 初始化地图
 * @param {string} mapId - HTML 中用于承载地图的 div 的 id
 */
export function initMap(mapId) {
    // 设置默认视图。可以根据需要调整中心点和缩放级别
    map = L.map(mapId).setView([30, 110], 4); 

    // 添加瓦片图层，这里使用 OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // 创建一个图层组来存放所有标记，方便统一管理
    markersGroup = L.layerGroup().addTo(map);

    // 初始化用于绘制路径的折线
    polyline = L.polyline(latlngs, { 
        color: '#3b82f6', // 蓝色
        weight: 3,
        opacity: 0.8
    }).addTo(map);
}


/**
 * 在地图上添加一个路径点（包括标记和路径更新）
 * @param {number} lat - 纬度
 * @param {number} lon - 经度
 * @param {string} popupText - 点击标记时显示的 HTML 内容
 */
export function addPathPoint(lat, lon, popupText) {
    if (!map) return;

    let adjustedLon = lon;

    if (latlngs.length > 0) {
        const [lat1, lon1] = latlngs[latlngs.length - 1];
        if (Math.abs(lat1-lat) == 0 && (Math.abs(lon1-lon)%360 == 0))
        {
            // console.log('repeat pos ,continu')
            return;
        }
    }

    // 如果已经有路径点，则根据经度差调整新点的经度，以确保最短路径
    if (latlngs.length > 0) {
        const lastPoint = latlngs[latlngs.length - 1];
        const lastLon = lastPoint[1];

        // 计算经度差
        let deltaLon = adjustedLon - lastLon;

        // 如果经度差大于180度，说明穿过180度经线向西走更短
        if (deltaLon > 180) {
            adjustedLon -= 360;
        } 
        // 如果经度差小于-180度，说明穿过180度经线向东走更短
        else if (deltaLon < -180) {
            adjustedLon += 360;
        }
        // 注意：此逻辑也适用于跨越0度经线的情况，因为它总是选择最短的经度路径
    }
    // console.log(lat,lon)
    // console.log(lat,adjustedLon)

    const point = [lat, adjustedLon];
    latlngs.push(point);

    // 创建一个标记并绑定弹窗
    const marker = L.marker(point).bindPopup(popupText);
    
    markersGroup.addLayer(marker);

    marker.openPopup();

    // 更新折线路径
    polyline.addLatLng(point);
}

/**
 * 清空地图上的所有标记和路径，为新的查询做准备
 */
export function clearMap() {
    if (!map) return;

    // 清空经纬度数组
    latlngs = [];
    
    // 清空标记图层
    markersGroup.clearLayers();
    
    // 重置折线
    polyline.setLatLngs(latlngs);
}

/**
 * 调整地图视野，使其能够完整显示整个路径
 */
export function fitMapView() {
    if (!map || latlngs.length === 0) return;

    // 如果只有一个点，则将视图中心设置在该点
    if (latlngs.length === 1) {
        map.setView(latlngs[0], 10); // 设置一个合适的缩放级别
    } else {
        // fitBounds 会自动计算合适的视图范围和缩放级别
        map.fitBounds(polyline.getBounds(), { padding: [100, 100] }); // 增加一些边距
    }
}
