(function (root) {
  const inBox = (lat, lon, south, west, north, east) =>
    lat >= south && lat <= north && lon >= west && lon <= east;
  const numerals = ['零', '一', '二', '三', '四', '五', '六', '七', '八'];
  const api = {
    viewForViewport({ zoom, lat, lon, current }) {
      if (zoom < 12.2) return 0;
      if (zoom >= 13.5 && inBox(lat, lon, 31.12, 121.62, 31.18, 121.70)) return 10;
      if (inBox(lat, lon, 31.17, 121.37, 31.29, 121.56)) {
        if (current >= 1 && current <= 5 && zoom >= 13.5) return current;
        return 9;
      }
      return 0;
    },
    dayName(day) { return '第' + (numerals[day] || String(day)) + '天'; }
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.JourneyMapContext = api;
})(typeof window !== 'undefined' ? window : globalThis);
