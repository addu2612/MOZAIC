// Advertiser Targeting Rules Repository
import { apiConnector } from "../../Connector";
import { advertiserTargetingEndpoints } from "../../Apis";
import {
  showValidationErrors,
  showSuccessToast,
  showLoadingToast,
} from "../../utils/toastUtils.jsx";
import { toast } from "react-hot-toast";

const {
  ADD_DEMOGRAPHIC_TARGETING,
  GET_DEMOGRAPHIC_TARGETING,
  UPDATE_DEMOGRAPHIC_TARGETING,
  DELETE_DEMOGRAPHIC_TARGETING,
  ADD_GEOGRAPHIC_TARGETING,
  GET_GEOGRAPHIC_TARGETING,
  UPDATE_GEOGRAPHIC_TARGETING,
  DELETE_GEOGRAPHIC_TARGETING,
  ADD_DEVICE_TARGETING,
  GET_DEVICE_TARGETING,
  UPDATE_DEVICE_TARGETING,
  DELETE_DEVICE_TARGETING,
  ADD_CONTEXTUAL_TARGETING,
  GET_CONTEXTUAL_TARGETING,
  UPDATE_CONTEXTUAL_TARGETING,
  DELETE_CONTEXTUAL_TARGETING,
  ADD_BEHAVIORAL_TARGETING,
  GET_BEHAVIORAL_TARGETING,
  UPDATE_BEHAVIORAL_TARGETING,
  DELETE_BEHAVIORAL_TARGETING,
  ADD_TIME_TARGETING,
  GET_TIME_TARGETING,
  UPDATE_TIME_TARGETING,
  DELETE_TIME_TARGETING,
  ADD_FREQUENCY_TARGETING,
  GET_FREQUENCY_TARGETING,
  UPDATE_FREQUENCY_TARGETING,
  DELETE_FREQUENCY_TARGETING,
  GET_ALL_TARGETING_RULES,
} = advertiserTargetingEndpoints;

// ==================== DEMOGRAPHIC TARGETING ====================
export function addDemographicTargeting(campaignId, data, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast("Adding demographic targeting...");
    try {
      const response = await apiConnector(
        ADD_DEMOGRAPHIC_TARGETING.type,
        `${ADD_DEMOGRAPHIC_TARGETING.url}/${campaignId}/targeting-rules/demographic`,
        data,
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 201) {
        showSuccessToast("Demographic targeting added successfully!");
        return response.data.data;
      }
      throw new Error(response.data.message);
    } catch (error) {
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

export function getDemographicTargeting(campaignId, token) {
  return async (dispatch) => {
    try {
      const response = await apiConnector(
        GET_DEMOGRAPHIC_TARGETING.type,
        `${GET_DEMOGRAPHIC_TARGETING.url}/${campaignId}/targeting-rules/demographic`,
        {},
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 200) {
        return Array.isArray(response.data.data) && response.data.data.length > 0 
          ? response.data.data[0] 
          : null;
      }
      throw new Error(response.data.message);
    } catch (error) {
      console.log("Get Demographic Targeting Error:", error);
      return null;
    }
  };
}

export function updateDemographicTargeting(campaignId, id, data, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast("Updating demographic targeting...");
    try {
      const response = await apiConnector(
        UPDATE_DEMOGRAPHIC_TARGETING.type,
        `${UPDATE_DEMOGRAPHIC_TARGETING.url}/${campaignId}/targeting-rules/demographic/${id}`,
        data,
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 200) {
        showSuccessToast("Demographic targeting updated successfully!");
        return response.data.data;
      }
      throw new Error(response.data.message);
    } catch (error) {
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

export function deleteDemographicTargeting(campaignId, id, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast("Deleting demographic targeting...");
    try {
      const response = await apiConnector(
        DELETE_DEMOGRAPHIC_TARGETING.type,
        `${DELETE_DEMOGRAPHIC_TARGETING.url}/${campaignId}/targeting-rules/demographic/${id}`,
        {},
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 200) {
        showSuccessToast("Demographic targeting deleted successfully!");
        return true;
      }
      throw new Error(response.data.message);
    } catch (error) {
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

// ==================== GEOGRAPHIC TARGETING ====================
export function addGeographicTargeting(campaignId, data, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast("Adding geographic targeting...");
    try {
      const response = await apiConnector(
        ADD_GEOGRAPHIC_TARGETING.type,
        `${ADD_GEOGRAPHIC_TARGETING.url}/${campaignId}/targeting-rules/geographic`,
        data,
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 201 || response.status === 200) {
        showSuccessToast("Geographic targeting added successfully!");
        return response.data.data;
      }
      throw new Error(response.data.message);
    } catch (error) {
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

export function getGeographicTargeting(campaignId, token) {
  return async (dispatch) => {
    try {
      const response = await apiConnector(
        GET_GEOGRAPHIC_TARGETING.type,
        `${GET_GEOGRAPHIC_TARGETING.url}/${campaignId}/targeting-rules/geographic`,
        {},
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 200) {
        return Array.isArray(response.data.data) && response.data.data.length > 0 
          ? response.data.data[0] 
          : null;
      }
      throw new Error(response.data.message);
    } catch (error) {
      console.log("Get Geographic Targeting Error:", error);
      return null;
    }
  };
}

export function updateGeographicTargeting(campaignId, id, data, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast("Updating geographic targeting...");
    try {
      const response = await apiConnector(
        UPDATE_GEOGRAPHIC_TARGETING.type,
        `${UPDATE_GEOGRAPHIC_TARGETING.url}/${campaignId}/targeting-rules/geographic/${id}`,
        data,
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 200) {
        showSuccessToast("Geographic targeting updated successfully!");
        return response.data.data;
      }
      throw new Error(response.data.message);
    } catch (error) {
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

export function deleteGeographicTargeting(campaignId, id, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast("Deleting geographic targeting...");
    try {
      const response = await apiConnector(
        DELETE_GEOGRAPHIC_TARGETING.type,
        `${DELETE_GEOGRAPHIC_TARGETING.url}/${campaignId}/targeting-rules/geographic/${id}`,
        {},
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 200) {
        showSuccessToast("Geographic targeting deleted successfully!");
        return true;
      }
      throw new Error(response.data.message);
    } catch (error) {
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

// ==================== DEVICE TARGETING ====================
export function addDeviceTargeting(campaignId, data, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast("Adding device targeting...");
    try {
      const response = await apiConnector(
        ADD_DEVICE_TARGETING.type,
        `${ADD_DEVICE_TARGETING.url}/${campaignId}/targeting-rules/device`,
        data,
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 201 || response.status === 200) {
        showSuccessToast("Device targeting added successfully!");
        return response.data.data;
      }
      throw new Error(response.data.message);
    } catch (error) {
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

export function getDeviceTargeting(campaignId, token) {
  return async (dispatch) => {
    try {
      const response = await apiConnector(
        GET_DEVICE_TARGETING.type,
        `${GET_DEVICE_TARGETING.url}/${campaignId}/targeting-rules/device`,
        {},
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 200) {
        return Array.isArray(response.data.data) && response.data.data.length > 0 
          ? response.data.data[0] 
          : null;
      }
      throw new Error(response.data.message);
    } catch (error) {
      console.log("Get Device Targeting Error:", error);
      return null;
    }
  };
}

export function updateDeviceTargeting(campaignId, id, data, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast("Updating device targeting...");
    try {
      const response = await apiConnector(
        UPDATE_DEVICE_TARGETING.type,
        `${UPDATE_DEVICE_TARGETING.url}/${campaignId}/targeting-rules/device/${id}`,
        data,
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 200) {
        showSuccessToast("Device targeting updated successfully!");
        return response.data.data;
      }
      throw new Error(response.data.message);
    } catch (error) {
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

export function deleteDeviceTargeting(campaignId, id, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast("Deleting device targeting...");
    try {
      const response = await apiConnector(
        DELETE_DEVICE_TARGETING.type,
        `${DELETE_DEVICE_TARGETING.url}/${campaignId}/targeting-rules/device/${id}`,
        {},
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 200) {
        showSuccessToast("Device targeting deleted successfully!");
        return true;
      }
      throw new Error(response.data.message);
    } catch (error) {
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

// ==================== CONTEXTUAL TARGETING ====================
export function addContextualTargeting(campaignId, data, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast("Adding contextual targeting...");
    try {
      const response = await apiConnector(
        ADD_CONTEXTUAL_TARGETING.type,
        `${ADD_CONTEXTUAL_TARGETING.url}/${campaignId}/targeting-rules/contextual`,
        data,
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 201 || response.status === 200) {
        showSuccessToast("Contextual targeting added successfully!");
        return response.data.data;
      }
      throw new Error(response.data.message);
    } catch (error) {
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

export function getContextualTargeting(campaignId, token) {
  return async (dispatch) => {
    try {
      const response = await apiConnector(
        GET_CONTEXTUAL_TARGETING.type,
        `${GET_CONTEXTUAL_TARGETING.url}/${campaignId}/targeting-rules/contextual`,
        {},
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 200) {
        return Array.isArray(response.data.data) && response.data.data.length > 0 
          ? response.data.data[0] 
          : null;
      }
      throw new Error(response.data.message);
    } catch (error) {
      console.log("Get Contextual Targeting Error:", error);
      return null;
    }
  };
}

export function updateContextualTargeting(campaignId, id, data, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast("Updating contextual targeting...");
    try {
      const response = await apiConnector(
        UPDATE_CONTEXTUAL_TARGETING.type,
        `${UPDATE_CONTEXTUAL_TARGETING.url}/${campaignId}/targeting-rules/contextual/${id}`,
        data,
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 200) {
        showSuccessToast("Contextual targeting updated successfully!");
        return response.data.data;
      }
      throw new Error(response.data.message);
    } catch (error) {
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

export function deleteContextualTargeting(campaignId, id, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast("Deleting contextual targeting...");
    try {
      const response = await apiConnector(
        DELETE_CONTEXTUAL_TARGETING.type,
        `${DELETE_CONTEXTUAL_TARGETING.url}/${campaignId}/targeting-rules/contextual/${id}`,
        {},
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 200) {
        showSuccessToast("Contextual targeting deleted successfully!");
        return true;
      }
      throw new Error(response.data.message);
    } catch (error) {
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

// ==================== BEHAVIORAL TARGETING ====================
export function addBehavioralTargeting(campaignId, data, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast("Adding behavioral targeting...");
    try {
      const response = await apiConnector(
        ADD_BEHAVIORAL_TARGETING.type,
        `${ADD_BEHAVIORAL_TARGETING.url}/${campaignId}/targeting-rules/behavioral`,
        data,
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 201 || response.status === 200) {
        showSuccessToast("Behavioral targeting added successfully!");
        return response.data.data;
      }
      throw new Error(response.data.message);
    } catch (error) {
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

export function getBehavioralTargeting(campaignId, token) {
  return async (dispatch) => {
    try {
      const response = await apiConnector(
        GET_BEHAVIORAL_TARGETING.type,
        `${GET_BEHAVIORAL_TARGETING.url}/${campaignId}/targeting-rules/behavioral`,
        {},
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 200) {
        return Array.isArray(response.data.data) && response.data.data.length > 0 
          ? response.data.data[0] 
          : null;
      }
      throw new Error(response.data.message);
    } catch (error) {
      console.log("Get Behavioral Targeting Error:", error);
      return null;
    }
  };
}

export function updateBehavioralTargeting(campaignId, id, data, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast("Updating behavioral targeting...");
    try {
      const response = await apiConnector(
        UPDATE_BEHAVIORAL_TARGETING.type,
        `${UPDATE_BEHAVIORAL_TARGETING.url}/${campaignId}/targeting-rules/behavioral/${id}`,
        data,
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 200) {
        showSuccessToast("Behavioral targeting updated successfully!");
        return response.data.data;
      }
      throw new Error(response.data.message);
    } catch (error) {
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

export function deleteBehavioralTargeting(campaignId, id, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast("Deleting behavioral targeting...");
    try {
      const response = await apiConnector(
        DELETE_BEHAVIORAL_TARGETING.type,
        `${DELETE_BEHAVIORAL_TARGETING.url}/${campaignId}/targeting-rules/behavioral/${id}`,
        {},
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 200) {
        showSuccessToast("Behavioral targeting deleted successfully!");
        return true;
      }
      throw new Error(response.data.message);
    } catch (error) {
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

// ==================== TIME TARGETING ====================
export function addTimeTargeting(campaignId, data, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast("Adding time targeting...");
    try {
      const response = await apiConnector(
        ADD_TIME_TARGETING.type,
        `${ADD_TIME_TARGETING.url}/${campaignId}/targeting-rules/time`,
        data,
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 201 || response.status === 200) {
        showSuccessToast("Time targeting added successfully!");
        return response.data.data;
      }
      throw new Error(response.data.message);
    } catch (error) {
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

export function getTimeTargeting(campaignId, token) {
  return async (dispatch) => {
    try {
      const response = await apiConnector(
        GET_TIME_TARGETING.type,
        `${GET_TIME_TARGETING.url}/${campaignId}/targeting-rules/time`,
        {},
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 200) {
        return Array.isArray(response.data.data) && response.data.data.length > 0 
          ? response.data.data[0] 
          : null;
      }
      throw new Error(response.data.message);
    } catch (error) {
      console.log("Get Time Targeting Error:", error);
      return null;
    }
  };
}

export function updateTimeTargeting(campaignId, id, data, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast("Updating time targeting...");
    try {
      const response = await apiConnector(
        UPDATE_TIME_TARGETING.type,
        `${UPDATE_TIME_TARGETING.url}/${campaignId}/targeting-rules/time/${id}`,
        data,
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 200) {
        showSuccessToast("Time targeting updated successfully!");
        return response.data.data;
      }
      throw new Error(response.data.message);
    } catch (error) {
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

export function deleteTimeTargeting(campaignId, id, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast("Deleting time targeting...");
    try {
      const response = await apiConnector(
        DELETE_TIME_TARGETING.type,
        `${DELETE_TIME_TARGETING.url}/${campaignId}/targeting-rules/time/${id}`,
        {},
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 200) {
        showSuccessToast("Time targeting deleted successfully!");
        return true;
      }
      throw new Error(response.data.message);
    } catch (error) {
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

// ==================== FREQUENCY TARGETING ====================
export function addFrequencyTargeting(campaignId, data, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast("Adding frequency targeting...");
    try {
      const response = await apiConnector(
        ADD_FREQUENCY_TARGETING.type,
        `${ADD_FREQUENCY_TARGETING.url}/${campaignId}/targeting-rules/frequency`,
        data,
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 201 || response.status === 200) {
        showSuccessToast("Frequency targeting added successfully!");
        return response.data.data;
      }
      throw new Error(response.data.message);
    } catch (error) {
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

export function getFrequencyTargeting(campaignId, token) {
  return async (dispatch) => {
    try {
      const response = await apiConnector(
        GET_FREQUENCY_TARGETING.type,
        `${GET_FREQUENCY_TARGETING.url}/${campaignId}/targeting-rules/frequency`,
        {},
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 200) {
        return Array.isArray(response.data.data) && response.data.data.length > 0 
          ? response.data.data[0] 
          : null;
      }
      throw new Error(response.data.message);
    } catch (error) {
      console.log("Get Frequency Targeting Error:", error);
      return null;
    }
  };
}

export function updateFrequencyTargeting(campaignId, id, data, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast("Updating frequency targeting...");
    try {
      const response = await apiConnector(
        UPDATE_FREQUENCY_TARGETING.type,
        `${UPDATE_FREQUENCY_TARGETING.url}/${campaignId}/targeting-rules/frequency/${id}`,
        data,
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 200) {
        showSuccessToast("Frequency targeting updated successfully!");
        return response.data.data;
      }
      throw new Error(response.data.message);
    } catch (error) {
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

export function deleteFrequencyTargeting(campaignId, id, token) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast("Deleting frequency targeting...");
    try {
      const response = await apiConnector(
        DELETE_FREQUENCY_TARGETING.type,
        `${DELETE_FREQUENCY_TARGETING.url}/${campaignId}/targeting-rules/frequency/${id}`,
        {},
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 200) {
        showSuccessToast("Frequency targeting deleted successfully!");
        return true;
      }
      throw new Error(response.data.message);
    } catch (error) {
      showValidationErrors(error);
      throw error;
    } finally {
      toast.dismiss(loadingToast);
    }
  };
}

// ==================== GET ALL TARGETING RULES ====================
export function getAllTargetingRules(campaignId, token) {
  return async (dispatch) => {
    try {
      const response = await apiConnector(
        GET_ALL_TARGETING_RULES.type,
        `${GET_ALL_TARGETING_RULES.url}/${campaignId}/targeting-rules`,
        {},
        { Authorization: `Bearer ${token}` }
      );
      if (response.status === 200) {
        return response.data.data;
      }
      throw new Error(response.data.message);
    } catch (error) {
      console.log("Get All Targeting Rules Error:", error);
      return null;
    }
  };
}
