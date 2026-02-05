// Publisher Ad Inventory Repository
// Handles ad slot/inventory management for publishers (Phase 4)
import { apiConnector } from '../../Connector.js';
import { publisherAdInventoryEndpoints } from '../../Apis.js';
import { toast } from 'react-hot-toast';

// Toast utilities
const showLoadingToast = (message) => toast.loading(message);
const showSuccessToast = (message) => toast.success(message, { duration: 3000 });
const showErrorToast = (message) => toast.error(message, { duration: 4000 });

const showValidationErrors = (error) => {
  if (error.response?.data?.message) {
    if (Array.isArray(error.response.data.message)) {
      error.response.data.message.forEach(msg => showErrorToast(msg));
    } else {
      showErrorToast(error.response.data.message);
    }
  } else {
    showErrorToast(error.message || 'An error occurred');
  }
};

// Hardcoded ad slot templates (as provided by user - will be replaced with API call in future)
export const AD_SLOT_TEMPLATES = [
  {
    id: "0a0d8304-b685-4814-965c-20108dcc61aa",
    name: "template_blackdecker_1200_1200",
    width: 1200,
    height: 1200,
    format: "BANNER",
    position: "IN_CONTENT"
  },
  {
    id: "1c3389bc-675f-4e84-8091-dc1b7ff2ba76",
    name: "template_blackdecker_1200_628",
    width: 1200,
    height: 628,
    format: "BANNER",
    position: "IN_CONTENT"
  },
  {
    id: "a5199fb4-1e54-4000-86c2-bf2a317eb6be",
    name: "template_blackdecker_1080_1350",
    width: 1080,
    height: 1350,
    format: "BANNER",
    position: "IN_CONTENT"
  },
  {
    id: "b7161632-604e-42ff-9761-583c455dabd1",
    name: "template_blackdecker_1080_1080",
    width: 1080,
    height: 1080,
    format: "BANNER",
    position: "ABOVE_FOLD"
  }
];

// ==================== AD INVENTORY MANAGEMENT ====================

/**
 * Create a new ad inventory slot
 * @param {Object} inventoryData - Inventory details {name, adSlotTemplateId, viewabilityScore, refreshInterval, lazyLoad, position}
 * @param {string} publisherId - Publisher ID
 * @param {string} websiteId - Website ID
 * @param {string} token - Auth token
 * @returns {Promise} - Created inventory data
 */
export function createAdInventory(inventoryData, publisherId, websiteId, token) {
  return async () => {
    const loadingToast = showLoadingToast('Creating ad slot...');
    try {
      // Build URL with path parameters
      const url = publisherAdInventoryEndpoints.CREATE_AD_INVENTORY.url
        .replace('{publisherId}', publisherId)
        .replace('{websiteId}', websiteId);

      const response = await apiConnector(
        publisherAdInventoryEndpoints.CREATE_AD_INVENTORY.type,
        url,
        inventoryData,
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Create Ad Inventory API response:', response);

      if (response.data.success) {
        showSuccessToast('Ad slot created successfully!');
        return response.data.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Create Ad Inventory API Error:', error);
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

/**
 * Get all ad inventory slots for a website
 * @param {string} publisherId - Publisher ID
 * @param {string} websiteId - Website ID
 * @param {string} token - Auth token
 * @returns {Promise} - List of ad inventory slots
 */
export function getAdInventoryList(publisherId, websiteId, token) {
  return async () => {
    try {
      const url = publisherAdInventoryEndpoints.GET_AD_INVENTORY_LIST.url
        .replace('{publisherId}', publisherId)
        .replace('{websiteId}', websiteId);

      const response = await apiConnector(
        publisherAdInventoryEndpoints.GET_AD_INVENTORY_LIST.type,
        url,
        {},
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Get Ad Inventory List API response:', response);

      if (response.data.success) {
        return response.data.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Get Ad Inventory List API Error:', error);
      showValidationErrors(error);
      throw error;
    }
  };
}

/**
 * Get specific ad inventory slot details
 * @param {string} publisherId - Publisher ID
 * @param {string} websiteId - Website ID
 * @param {string} adSlotId - Ad Slot ID
 * @param {string} token - Auth token
 * @returns {Promise} - Ad inventory details
 */
export function getAdInventory(publisherId, websiteId, adSlotId, token) {
  return async () => {
    try {
      const url = publisherAdInventoryEndpoints.GET_AD_INVENTORY.url
        .replace('{publisherId}', publisherId)
        .replace('{websiteId}', websiteId)
        .replace('{adSlotId}', adSlotId);

      const response = await apiConnector(
        publisherAdInventoryEndpoints.GET_AD_INVENTORY.type,
        url,
        {},
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Get Ad Inventory API response:', response);

      if (response.data.success) {
        return response.data.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Get Ad Inventory API Error:', error);
      showValidationErrors(error);
      throw error;
    }
  };
}

/**
 * Update ad inventory slot
 * @param {Object} updateData - Updated inventory details
 * @param {string} publisherId - Publisher ID
 * @param {string} websiteId - Website ID
 * @param {string} adSlotId - Ad Slot ID
 * @param {string} token - Auth token
 * @returns {Promise} - Updated inventory data
 */
export function updateAdInventory(updateData, publisherId, websiteId, adSlotId, token) {
  return async () => {
    const loadingToast = showLoadingToast('Updating ad slot...');
    try {
      const url = publisherAdInventoryEndpoints.UPDATE_AD_INVENTORY.url
        .replace('{publisherId}', publisherId)
        .replace('{websiteId}', websiteId)
        .replace('{adSlotId}', adSlotId);

      const response = await apiConnector(
        publisherAdInventoryEndpoints.UPDATE_AD_INVENTORY.type,
        url,
        updateData,
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Update Ad Inventory API response:', response);

      if (response.data.success) {
        showSuccessToast('Ad slot updated successfully!');
        return response.data.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Update Ad Inventory API Error:', error);
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

/**
 * Delete ad inventory slot
 * @param {string} publisherId - Publisher ID
 * @param {string} websiteId - Website ID
 * @param {string} adSlotId - Ad Slot ID
 * @param {string} token - Auth token
 * @returns {Promise} - Deletion result
 */
export function deleteAdInventory(publisherId, websiteId, adSlotId, token) {
  return async () => {
    const loadingToast = showLoadingToast('Deleting ad slot...');
    try {
      const url = publisherAdInventoryEndpoints.DELETE_AD_INVENTORY.url
        .replace('{publisherId}', publisherId)
        .replace('{websiteId}', websiteId)
        .replace('{adSlotId}', adSlotId);

      const response = await apiConnector(
        publisherAdInventoryEndpoints.DELETE_AD_INVENTORY.type,
        url,
        {},
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Delete Ad Inventory API response:', response);

      if (response.data.success) {
        showSuccessToast('Ad slot deleted successfully!');
        return response.data.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Delete Ad Inventory API Error:', error);
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

/**
 * Toggle ad inventory active status
 * @param {string} publisherId - Publisher ID
 * @param {string} websiteId - Website ID
 * @param {string} adSlotId - Ad Slot ID
 * @param {string} token - Auth token
 * @returns {Promise} - Toggle result
 */
export function toggleAdInventoryStatus(publisherId, websiteId, adSlotId, token) {
  return async () => {
    const loadingToast = showLoadingToast('Toggling ad slot status...');
    try {
      const url = publisherAdInventoryEndpoints.TOGGLE_AD_INVENTORY_STATUS.url
        .replace('{publisherId}', publisherId)
        .replace('{websiteId}', websiteId)
        .replace('{adSlotId}', adSlotId);

      const response = await apiConnector(
        publisherAdInventoryEndpoints.TOGGLE_AD_INVENTORY_STATUS.type,
        url,
        {},
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Toggle Ad Inventory Status API response:', response);

      if (response.data.success) {
        showSuccessToast('Ad slot status updated!');
        return response.data.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Toggle Ad Inventory Status API Error:', error);
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}
