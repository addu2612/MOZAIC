// Publisher Management Repository
// Handles publisher profile, tiers, websites, and floor price rules (Phase 3)
import { apiConnector } from '../../Connector.js';
import { publisherEndpoints, publisherWebsiteEndpoints, publisherFloorPriceEndpoints } from '../../Apis.js';
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

// ==================== TIER MANAGEMENT ====================

/**
 * Get all available publisher tiers
 * @param {string} token - Auth token
 * @returns {Promise} - List of all available tiers
 */
export function getAllTiers(token) {
  return async () => {
    try {
      const response = await apiConnector(
        publisherEndpoints.GET_ALL_TIERS.type,
        publisherEndpoints.GET_ALL_TIERS.url,
        {},
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Get All Tiers API response:', response);

      if (response.data.success) {
        return response.data.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Get All Tiers API Error:', error);
      showValidationErrors(error);
      throw error;
    }
  };
}

/**
 * Get current publisher tier information
 * @param {string} token - Auth token
 * @returns {Promise} - Current tier details with commission rate
 */
export function getCurrentTier(token) {
  return async () => {
    try {
      const response = await apiConnector(
        publisherEndpoints.GET_CURRENT_TIER.type,
        publisherEndpoints.GET_CURRENT_TIER.url,
        {},
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Get Current Tier API response:', response);

      if (response.data.success) {
        return response.data.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Get Current Tier API Error:', error);
      showValidationErrors(error);
      throw error;
    }
  };
}

// ==================== WEBSITE MANAGEMENT ====================

/**
 * Create a new website for the publisher
 * @param {Object} websiteData - Website details {url, websiteName, publisherId, categoryIds, description}
 * @param {string} token - Auth token
 * @returns {Promise} - Created website data
 */
export function createWebsite(websiteData, token) {
  return async () => {
    const loadingToast = showLoadingToast('Creating website...');
    try {
      // Ensure required fields according to CreateWebsiteDto
      const payload = {
        url: websiteData.url,
        websiteName: websiteData.websiteName || websiteData.name,
        publisherId: websiteData.publisherId,
        categoryIds: websiteData.categoryIds || [],
        description: websiteData.description
      };

      const response = await apiConnector(
        publisherWebsiteEndpoints.CREATE_WEBSITE.type,
        publisherWebsiteEndpoints.CREATE_WEBSITE.url,
        payload,
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Create Website API response:', response);

      if (response.data.success) {
        showSuccessToast('Website created successfully!');
        return response.data.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Create Website API Error:', error);
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

/**
 * Get all websites for a publisher
 * @param {string} publisherId - Publisher ID
 * @param {string} token - Auth token
 * @returns {Promise} - List of all websites
 */
export function getWebsites(publisherId, token) {
  return async () => {
    try {
      const response = await apiConnector(
        publisherWebsiteEndpoints.GET_WEBSITES.type,
        publisherWebsiteEndpoints.GET_WEBSITES.url.replace('{id}', publisherId),
        {},
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Get Websites API response:', response);

      if (response.data.success) {
        return response.data.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Get Websites API Error:', error);
      showValidationErrors(error);
      throw error;
    }
  };
}

/**
 * Get a specific website by ID or URL
 * @param {string} publisherId - Publisher ID
 * @param {string} data - Website ID or URL
 * @param {string} type - 'id' or 'url'
 * @param {string} token - Auth token
 * @returns {Promise} - Website details
 */
export function getWebsiteByIdOrUrl(publisherId, data, type, token) {
  return async () => {
    try {
      // Build URL with path parameters and query parameter for type
      const url = publisherWebsiteEndpoints.GET_WEBSITE_BY_ID_OR_URL.url
        .replace('{publisherId}', publisherId)
        .replace('{data}', data) + `?type=${type}`;

      const response = await apiConnector(
        publisherWebsiteEndpoints.GET_WEBSITE_BY_ID_OR_URL.type,
        url,
        {},
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Get Website By ID/URL API response:', response);

      if (response.data.success) {
        return response.data.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Get Website By ID/URL API Error:', error);
      showValidationErrors(error);
      throw error;
    }
  };
}

/**
 * Activate a website by ID
 * @param {string} publisherId - Publisher ID
 * @param {string} websiteId - Website ID
 * @param {string} token - Auth token
 * @returns {Promise} - Activation result
 */
export function activateWebsite(publisherId, websiteId, token) {
  return async () => {
    const loadingToast = showLoadingToast('Activating website...');
    try {
      const response = await apiConnector(
        publisherWebsiteEndpoints.ACTIVATE_WEBSITE.type,
        publisherWebsiteEndpoints.ACTIVATE_WEBSITE.url
          .replace('{publisherId}', publisherId)
          .replace('{websiteId}', websiteId),
        {},
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Activate Website API response:', response);

      if (response.data.success) {
        showSuccessToast('Website activated successfully!');
        return response.data.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Activate Website API Error:', error);
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

/**
 * Delete a website by ID
 * @param {string} publisherId - Publisher ID
 * @param {string} websiteId - Website ID
 * @param {string} token - Auth token
 * @returns {Promise} - Deletion result
 */
export function deleteWebsite(publisherId, websiteId, token) {
  return async () => {
    const loadingToast = showLoadingToast('Deleting website...');
    try {
      const response = await apiConnector(
        publisherWebsiteEndpoints.DELETE_WEBSITE.type,
        publisherWebsiteEndpoints.DELETE_WEBSITE.url
          .replace('{publisherId}', publisherId)
          .replace('{websiteId}', websiteId),
        {},
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Delete Website API response:', response);

      if (response.data.success) {
        showSuccessToast('Website deleted successfully!');
        return response.data.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Delete Website API Error:', error);
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

// ==================== FLOOR PRICE RULES ====================

/**
 * Create a new floor price rule for a website
 * @param {Object} ruleData - Floor price rule details {basePrice, inventoryId, publisherId, websiteId, startDate, endDate, currency}
 * @param {string} token - Auth token
 * @returns {Promise} - Created rule data
 */
export function createFloorPriceRule(ruleData, token) {
  return async () => {
    const loadingToast = showLoadingToast('Creating floor price rule...');
    try {
      // Ensure required fields according to CreateFloorPriceDto
      const payload = {
        basePrice: ruleData.basePrice,
        currency: ruleData.currency || 'USD',
        inventoryId: ruleData.inventoryId,
        publisherId: ruleData.publisherId,
        websiteId: ruleData.websiteId,
        startDate: ruleData.startDate,
        endDate: ruleData.endDate
      };

      const response = await apiConnector(
        publisherFloorPriceEndpoints.CREATE_FLOOR_PRICE.type,
        publisherFloorPriceEndpoints.CREATE_FLOOR_PRICE.url,
        payload,
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Create Floor Price Rule API response:', response);

      if (response.data.success) {
        showSuccessToast('Floor price rule created successfully!');
        return response.data.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Create Floor Price Rule API Error:', error);
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

/**
 * Update a floor price rule
 * @param {Object} updateData - Updated rule details (must include id in the payload)
 * @param {string} token - Auth token
 * @returns {Promise} - Updated rule data
 */
export function updateFloorPriceRule(updateData, token) {
  return async () => {
    const loadingToast = showLoadingToast('Updating floor price rule...');
    try {
      const response = await apiConnector(
        publisherFloorPriceEndpoints.UPDATE_FLOOR_PRICE.type,
        publisherFloorPriceEndpoints.UPDATE_FLOOR_PRICE.url,
        updateData,
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Update Floor Price Rule API response:', response);

      if (response.data.success) {
        showSuccessToast('Floor price rule updated successfully!');
        return response.data.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Update Floor Price Rule API Error:', error);
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

/**
 * Get all floor price rules for an adslot
 * @param {string} publisherId - Publisher ID
 * @param {string} adSlotId - Ad Slot ID
 * @param {string} token - Auth token
 * @returns {Promise} - List of floor price rules
 */
export function getFloorPriceRules(publisherId, adSlotId, token) {
  return async () => {
    try {
      const response = await apiConnector(
        publisherFloorPriceEndpoints.GET_FLOOR_PRICES.type,
        publisherFloorPriceEndpoints.GET_FLOOR_PRICES.url
          .replace('{publisherId}', publisherId)
          .replace('{adSlotId}', adSlotId),
        {},
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Get Floor Price Rules API response:', response);

      if (response.data.success) {
        return response.data.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Get Floor Price Rules API Error:', error);
      showValidationErrors(error);
      throw error;
    }
  };
}

/**
 * Get single floor price rule for an adslot
 * @param {string} publisherId - Publisher ID
 * @param {string} adSlotId - Ad Slot ID
 * @param {string} ruleId - Rule ID
 * @param {string} token - Auth token
 * @returns {Promise} - Floor price rule details
 */
export function getSingleFloorPriceRule(publisherId, adSlotId, ruleId, token) {
  return async () => {
    try {
      const response = await apiConnector(
        publisherFloorPriceEndpoints.GET_SINGLE_FLOOR_PRICE.type,
        publisherFloorPriceEndpoints.GET_SINGLE_FLOOR_PRICE.url
          .replace('{publisherId}', publisherId)
          .replace('{adSlotId}', adSlotId)
          .replace('{floorPriceId}', ruleId),
        {},
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Get Single Floor Price Rule API response:', response);

      if (response.data.success) {
        return response.data.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Get Single Floor Price Rule API Error:', error);
      showValidationErrors(error);
      throw error;
    }
  };
}

/**
 * Delete a floor price rule
 * @param {string} publisherId - Publisher ID
 * @param {string} ruleId - Rule ID
 * @param {string} token - Auth token
 * @returns {Promise} - Deletion result
 */
export function deleteFloorPriceRule(publisherId, ruleId, token) {
  return async () => {
    const loadingToast = showLoadingToast('Deleting floor price rule...');
    try {
      const response = await apiConnector(
        publisherFloorPriceEndpoints.DELETE_FLOOR_PRICE.type,
        publisherFloorPriceEndpoints.DELETE_FLOOR_PRICE.url
          .replace('{publisherId}', publisherId)
          .replace('{floorPriceId}', ruleId),
        {},
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Delete Floor Price Rule API response:', response);

      if (response.data.success) {
        showSuccessToast('Floor price rule deleted successfully!');
        return response.data.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Delete Floor Price Rule API Error:', error);
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}
