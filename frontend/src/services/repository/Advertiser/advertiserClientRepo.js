

import { apiConnector } from '../../Connector.js';
import { advertiserClientEndpoints } from '../../Apis';
import { showValidationErrors, showSuccessToast, showLoadingToast } from '../../utils/toastUtils.jsx';
import { toast } from 'react-hot-toast';

const {
  CREATE_CLIENT,
  GET_ALL_CLIENTS,
  GET_CLIENT_BY_ID,
  UPDATE_CLIENT,
  ASSIGN_CAMPAIGNS,
} = advertiserClientEndpoints;

export function createClient(clientData, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast('Creating client...');
    try {
      const response = await apiConnector(
        CREATE_CLIENT.type,
        CREATE_CLIENT.url,
        clientData,
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Create Client API response:', response);

      if (response.data.success || response.status === 201) {
        showSuccessToast('Client created successfully!');
        return response.data.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Create Client API Error:', error);
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}


export function getAllClients(token) {
  return async (dispatch) => {
    try {
      const response = await apiConnector(
        GET_ALL_CLIENTS.type,
        GET_ALL_CLIENTS.url,
        {},
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Get All Clients API response:', response);

      if (response.data.success || response.status === 200) {
        return response.data.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Get All Clients API Error:', error);
      showValidationErrors(error);
      return [];
    }
  };
}


export function getClientById(clientId, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast('Loading client details...');
    try {
      const response = await apiConnector(
        GET_CLIENT_BY_ID.type,
        `${GET_CLIENT_BY_ID.url}/${clientId}`,
        {},
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Get Client By ID API response:', response);

      if (response.data.success || response.status === 200) {
        return response.data.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Get Client By ID API Error:', error);
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}


export function updateClient(clientId, clientData, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast('Updating client...');
    try {
      const response = await apiConnector(
        UPDATE_CLIENT.type,
        `${UPDATE_CLIENT.url}/${clientId}`,
        clientData,
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Update Client API response:', response);

      if (response.data.success || response.status === 200) {
        showSuccessToast('Client updated successfully!');
        return response.data.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Update Client API Error:', error);
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}


export function assignCampaigns(clientId, campaignIds, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast('Assigning campaigns...');
    try {
      const response = await apiConnector(
        ASSIGN_CAMPAIGNS.type,
        `${ASSIGN_CAMPAIGNS.url}/${clientId}/assign-campaigns`,
        { campaignIds },
        {
          Authorization: `Bearer ${token}`,
        }
      );

      console.log('Assign Campaigns API response:', response);

      if (response.data.success || response.status === 200) {
        showSuccessToast('Campaigns assigned successfully!');
        return response.data.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Assign Campaigns API Error:', error);
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}