/**
 * SafarSaathi Admin Upload Controller
 * Handles admin-exclusive file upload for sponsor video ads, custom promos,
 * products/cushions, media banners, and documents directly from admin.html.
 */

function handleAdminUpload(file, type, metadata) {
  return new Promise((resolve, reject) => {
    if (!file) return reject('No file provided');
    const reader = new FileReader();
    reader.onload = function(e) {
      const payload = {
        data: e.target.result,
        name: file.name,
        type: type || 'video',
        metadata: metadata || {},
        timestamp: new Date().toISOString()
      };
      resolve(payload);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

if (typeof module !== 'undefined') {
  module.exports = { handleAdminUpload };
}
