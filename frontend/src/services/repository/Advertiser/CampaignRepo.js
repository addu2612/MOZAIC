// Advertiser Campaign Management Repository
import { apiConnector } from '../../Connector';
import { advertiserCampaignEndpoints } from '../../Apis';
import { showValidationErrors, showSuccessToast, showLoadingToast } from '../../utils/toastUtils.jsx';
import { toast } from 'react-hot-toast';
import { assignCampaigns } from './advertiserClientRepo.js';

const {
  CREATE_CAMPAIGN,
  GET_ALL_CAMPAIGNS,
  UPDATE_CAMPAIGN,
  GET_CAMPAIGN,
  DELETE_CAMPAIGN,
} = advertiserCampaignEndpoints;

/**
 * Create a new campaign
 * @param {string} advertiserId - Advertiser ID
 * @param {Object} campaignData - Campaign information
 * @param {string} token - Auth token
 */
export function createCampaign(advertiserId, campaignData, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast('Creating campaign...');
    try {
      const response = await apiConnector(
        CREATE_CAMPAIGN.type,
        `${CREATE_CAMPAIGN.url}/${advertiserId}/campaign`,
        campaignData,
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Create Campaign API response:', response);

      if (response.data.success || response.status === 200) {
        const createdCampaign = response.data.data;
        
        // Assign campaign to client
        try {
          await dispatch(assignCampaigns(campaignData.clientId, [createdCampaign.id], token));
        } catch (assignError) {
          console.log('Assign campaign to client failed:', assignError);
          // Continue even if assignment fails
        }
        
        showSuccessToast('Campaign created successfully!');
        return createdCampaign;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Create Campaign API Error:', error);
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

/**
 * Get all campaigns for the advertiser
 * @param {string} advertiserId - Advertiser ID
 * @param {string} token - Auth token
 */
export function getAllCampaigns(advertiserId, token) {
  return async (dispatch) => {
    try {
      const response = await apiConnector(
        GET_ALL_CAMPAIGNS.type,
        `${GET_ALL_CAMPAIGNS.url}/${advertiserId}/campaign`,
        {},
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Get All Campaigns API response:', response);

      if (response.data.success || response.status === 200) {
        return response.data.data.items || [];
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Get All Campaigns API Error:', error);
      showValidationErrors(error);
      return [];
    }
  };
}

/**
 * Get campaign by ID
 * @param {string} advertiserId - Advertiser ID
 * @param {string} campaignId - Campaign ID
 * @param {string} token - Auth token
 */
export function getCampaignById(advertiserId, campaignId, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast('Loading campaign details...');
    try {
      const response = await apiConnector(
        GET_CAMPAIGN.type,
        `${GET_CAMPAIGN.url}/${advertiserId}/campaign/${campaignId}`,
        {},
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Get Campaign By ID API response:', response);

      if (response.data.success || response.status === 200) {
        return response.data.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Get Campaign By ID API Error:', error);
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

/**
 * Update campaign information
 * @param {string} advertiserId - Advertiser ID
 * @param {string} campaignId - Campaign ID
 * @param {Object} campaignData - Updated campaign data
 * @param {string} token - Auth token
 */
export function updateCampaign(advertiserId, campaignId, campaignData, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast('Updating campaign...');
    try {
      const response = await apiConnector(
        UPDATE_CAMPAIGN.type,
        `${UPDATE_CAMPAIGN.url}/${advertiserId}/campaign/${campaignId}`,
        campaignData,
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Update Campaign API response:', response);

      if (response.data.success || response.status === 200) {
        showSuccessToast('Campaign updated successfully!');
        return response.data.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Update Campaign API Error:', error);
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

/**
 * Delete campaign
 * @param {string} advertiserId - Advertiser ID
 * @param {string} campaignId - Campaign ID
 * @param {string} token - Auth token
 */
export function deleteCampaign(advertiserId, campaignId, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast('Deleting campaign...');
    try {
      const response = await apiConnector(
        DELETE_CAMPAIGN.type,
        `${DELETE_CAMPAIGN.url}/${advertiserId}/campaign/${campaignId}`,
        {},
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Delete Campaign API response:', response);

      if (response.data.success || response.status === 200) {
        showSuccessToast('Campaign deleted successfully!');
        return true;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Delete Campaign API Error:', error);
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}