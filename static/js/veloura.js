/*
 * VELOURA — Frontend behaviour
 */

document.addEventListener('DOMContentLoaded', function () {
  // Initialize Lucide icons
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }

  // Re-render Lucide icons after dynamic HTML updates
  window.refreshIcons = function () {
    if (typeof lucide !== 'undefined') {
      lucide.createIcons();
    }
  };

  // Sidebar toggle (mobile)
  var menuToggle = document.getElementById('menuToggle');
  var sidebar = document.getElementById('sidebar');
  var overlay = document.getElementById('sidebarOverlay');

  if (menuToggle && sidebar && overlay) {
    function toggleSidebar() {
      sidebar.classList.toggle('open');
      overlay.classList.toggle('open');
    }
    menuToggle.addEventListener('click', toggleSidebar);
    overlay.addEventListener('click', toggleSidebar);
  }

  // Sidebar user profile card (revealed when logged in)
  var sidebarUser = document.getElementById('sidebarUser');
  if (sidebarUser) {
    sidebarUser.style.display = 'block';
  }

  // Auto-dismiss alerts after 6 seconds
  setTimeout(function () {
    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
      var bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    });
  }, 6000);

  // Confirmation for destructive actions
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      if (!confirm(el.getAttribute('data-confirm'))) {
        e.preventDefault();
      }
    });
  });

  // Show loading overlay on form submit (non-AJAX full postbacks)
  var loadingOverlay = document.getElementById('loadingOverlay');
  document.querySelectorAll('form').forEach(function (form) {
    form.addEventListener('submit', function () {
      if (loadingOverlay) loadingOverlay.style.display = 'flex';
    });
  });
});
