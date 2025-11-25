// Offline Support and Service Worker Registration
import { initPerformanceMonitoring } from '@/utils/performanceMonitoring';

class OfflineSupport {
  constructor() {
    this.isOnline = navigator.onLine;
    this.offlineQueue = [];
    this.init();
  }
  
  init() {
    // Register service worker
    this.registerServiceWorker();
    
    // Set up online/offline event listeners
    this.setupEventListeners();
    
    // Initialize performance monitoring
    initPerformanceMonitoring();
    
    // Set up offline detection
    this.setupOfflineDetection();
  }
  
  // Register service worker
  async registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.register('/sw.js');
        console.log('Service Worker registered successfully:', registration);
        
        // Handle updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              // New service worker is available
              this.showUpdateNotification();
            }
          });
        });
        
      } catch (error) {
        console.error('Service Worker registration failed:', error);
      }
    }
  }
  
  // Set up event listeners
  setupEventListeners() {
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.handleOnline();
    });
    
    window.addEventListener('offline', () => {
      this.isOnline = false;
      this.handleOffline();
    });
    
    // Listen for service worker messages
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.addEventListener('message', (event) => {
        this.handleServiceWorkerMessage(event.data);
      });
    }
  }
  
  // Handle online event
  handleOnline() {
    console.log('Back online');
    
    // Show online notification
    this.showNotification('You are back online', 'success');
    
    // Process queued requests
    this.processOfflineQueue();
    
    // Sync any pending data
    this.syncPendingData();
  }
  
  // Handle offline event
  handleOffline() {
    console.log('Gone offline');
    
    // Show offline notification
    this.showNotification('You are offline. Some features may not be available.', 'warning');
    
    // Enable offline mode
    this.enableOfflineMode();
  }
  
  // Set up offline detection
  setupOfflineDetection() {
    // Check connection status periodically
    setInterval(() => {
      const wasOnline = this.isOnline;
      this.isOnline = navigator.onLine;
      
      if (wasOnline && !this.isOnline) {
        this.handleOffline();
      } else if (!wasOnline && this.isOnline) {
        this.handleOnline();
      }
    }, 1000);
  }
  
  // Process offline queue
  async processOfflineQueue() {
    const queue = JSON.parse(localStorage.getItem('offline_queue') || '[]');
    if (queue.length === 0) return;
    
    console.log(`Processing ${queue.length} queued requests`);
    
    for (const request of queue) {
      try {
        await this.processQueuedRequest(request);
        console.log('Processed queued request:', request.url);
      } catch (error) {
        console.error('Failed to process queued request:', error);
      }
    }
    
    // Clear the queue
    localStorage.removeItem('offline_queue');
  }
  
  // Process individual queued request
  async processQueuedRequest(request) {
    const response = await fetch(request.url, {
      method: request.method,
      headers: request.headers,
      body: request.body
    });
    
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    
    return response.json();
  }
  
  // Sync pending data
  async syncPendingData() {
    // Sync any pending changes
    const pendingChanges = JSON.parse(localStorage.getItem('pending_changes') || '[]');
    
    for (const change of pendingChanges) {
      try {
        await this.syncChange(change);
        console.log('Synced change:', change);
      } catch (error) {
        console.error('Failed to sync change:', error);
      }
    }
    
    // Clear synced changes
    localStorage.removeItem('pending_changes');
  }
  
  // Sync individual change
  async syncChange(change) {
    const response = await fetch(change.url, {
      method: change.method,
      headers: change.headers,
      body: change.body
    });
    
    if (!response.ok) {
      throw new Error(`Sync failed: ${response.status}`);
    }
    
    return response.json();
  }
  
  // Enable offline mode
  enableOfflineMode() {
    // Show offline indicator
    this.showOfflineIndicator();
    
    // Disable certain features
    this.disableOfflineFeatures();
  }
  
  // Show offline indicator
  showOfflineIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'offline-indicator';
    indicator.className = 'fixed top-0 left-0 right-0 bg-yellow-500 text-white text-center py-2 z-50';
    indicator.textContent = 'You are offline. Some features may not be available.';
    document.body.appendChild(indicator);
  }
  
  // Hide offline indicator
  hideOfflineIndicator() {
    const indicator = document.getElementById('offline-indicator');
    if (indicator) {
      indicator.remove();
    }
  }
  
  // Disable offline features
  disableOfflineFeatures() {
    // Disable forms that require network
    const forms = document.querySelectorAll('form[data-requires-network]');
    forms.forEach(form => {
      form.style.opacity = '0.5';
      form.style.pointerEvents = 'none';
    });
  }
  
  // Enable offline features
  enableOfflineFeatures() {
    // Enable forms
    const forms = document.querySelectorAll('form[data-requires-network]');
    forms.forEach(form => {
      form.style.opacity = '1';
      form.style.pointerEvents = 'auto';
    });
  }
  
  // Show notification
  showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
      type === 'success' ? 'bg-green-500 text-white' :
      type === 'warning' ? 'bg-yellow-500 text-white' :
      type === 'error' ? 'bg-red-500 text-white' :
      'bg-blue-500 text-white'
    }`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
      notification.remove();
    }, 5000);
  }
  
  // Show update notification
  showUpdateNotification() {
    const notification = document.createElement('div');
    notification.className = 'fixed bottom-4 right-4 p-4 bg-blue-500 text-white rounded-lg shadow-lg z-50';
    notification.innerHTML = `
      <div class="flex items-center space-x-3">
        <span>New version available!</span>
        <button onclick="window.location.reload()" class="bg-white text-blue-500 px-3 py-1 rounded text-sm">
          Update
        </button>
      </div>
    `;
    document.body.appendChild(notification);
  }
  
  // Handle service worker messages
  handleServiceWorkerMessage(data) {
    switch (data.type) {
      case 'CACHE_UPDATED':
        console.log('Cache updated:', data.cacheName);
        break;
      case 'OFFLINE_REQUEST':
        console.log('Offline request queued:', data.request);
        break;
      case 'SYNC_COMPLETE':
        console.log('Background sync complete:', data.result);
        break;
      default:
        console.log('Unknown service worker message:', data);
    }
  }
  
  // Queue request for offline processing
  queueRequest(request) {
    const queue = JSON.parse(localStorage.getItem('offline_queue') || '[]');
    queue.push({
      ...request,
      timestamp: Date.now()
    });
    localStorage.setItem('offline_queue', JSON.stringify(queue));
  }
  
  // Queue change for sync
  queueChange(change) {
    const changes = JSON.parse(localStorage.getItem('pending_changes') || '[]');
    changes.push({
      ...change,
      timestamp: Date.now()
    });
    localStorage.setItem('pending_changes', JSON.stringify(changes));
  }
  
  // Check if online
  isOnline() {
    return this.isOnline;
  }
  
  // Get offline status
  getOfflineStatus() {
    return {
      isOnline: this.isOnline,
      queuedRequests: JSON.parse(localStorage.getItem('offline_queue') || '[]').length,
      pendingChanges: JSON.parse(localStorage.getItem('pending_changes') || '[]').length,
    };
  }
}

// Create singleton instance
const offlineSupport = new OfflineSupport();

export default offlineSupport;



