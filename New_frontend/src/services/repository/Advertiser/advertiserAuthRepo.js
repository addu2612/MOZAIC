// Advertiser Authentication Repository
// This repository handles all advertiser authentication flows including registration, login, MFA, and password management
import { apiConnector } from '../../Connector.js';
import {
  setAccount,
  setAccountAfterRegister,
  setDFeature,
} from '../../../app/DashboardSlice.js';
import { authAdvertiserEndpoints } from '../../Apis.js';
import { showValidationErrors, showSuccessToast, showLoadingToast } from '../../utils/toastUtils.jsx';
import { toast } from 'react-hot-toast';

const {
  SIGNUP,
  LOGIN,
  VERIFY_EMAIL,
  RESEND_VERIFICATION,
  PROFILE,
  VERIFY_MFA,
  TOGGLE_MFA,
  UPDATE_PROFILE,
  FORGOT_PASSWORD,
  VALIDATE_RESET_TOKEN,
  RESET_PASSWORD,
} = authAdvertiserEndpoints;

/**
 * Register a new advertiser
 * @param {string} name - Advertiser's name
 * @param {string} email - Advertiser's email
 * @param {string} password - Advertiser's password
 * @param {string} companyName - Company name
 * @param {string} mobile - Mobile number (10-digit)
 * @param {string} hqLocation - Headquarters location
 * @param {string} companySize - Company size (enum)
 * @param {Function} navigate - React Router navigate function
 */
export function registerAdvertiser(
  name,
  email,
  password,
  companyName,
  mobile,
  hqLocation,
  companySize,
  navigate,
) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast('Registering advertiser...');
    try {
      const response = await apiConnector(SIGNUP.type, SIGNUP.url, {
        name,
        email,
        password,
        companyName,
        mobile,
        hqLocation,
        companySize,
      });

      console.log('Advertiser Registration API response:', response);

      if (response.data.success) {
        showSuccessToast('Registration Successful! Please verify your email.');
        
        // Extract advertiser data from response
        const advertiserData = response.data.data.advertiser;
        
        const temp = {
          id: advertiserData.id,
          uname: advertiserData.name,
          uemail: advertiserData.email,
          mobile: advertiserData.mobile,
          companyName: advertiserData.companyName,
          hqLocation: advertiserData.hqLocation,
          companySize: advertiserData.companySize,
          role: 'advertiser',
          role_id: 2,
          emailVerified: false,
          mfaEnabled: advertiserData.mfaEnabled || false,
          status: advertiserData.status,
        };
        
        // Store email for resend verification
        localStorage.setItem('pending_verification_email', advertiserData.email);
        
        dispatch(setAccountAfterRegister(temp));
        navigate('/advertiser/verify-email');
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Advertiser Registration API Error:', error);
      showValidationErrors(error);
    }
    toast.dismiss(loadingToast);
  };
}

/**
 * Verify advertiser email with token
 * @param {string} token - Verification token from email
 * @param {Function} navigate - React Router navigate function
 */
export function verifyAdvertiserEmail(token, navigate) {
  return async (dispatch) => {
    const toastId = showLoadingToast('Verifying email...');
    try {
      const response = await apiConnector(
        VERIFY_EMAIL.type,
        `${VERIFY_EMAIL.url}/${token}`,
      );

      console.log('Email Verification API response:', response);

      if (response.data.success) {
        showSuccessToast('Email verified successfully! You can now login.');
        // Clear the pending verification email from localStorage
        localStorage.removeItem('pending_verification_email');
        navigate('/advertiser/login');
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Email Verification API Error:', error);
      showValidationErrors(error);
    }
    toast.dismiss(toastId);
  };
}

/**
 * Login advertiser
 * @param {string} email - Advertiser's email
 * @param {string} password - Advertiser's password
 * @param {Function} navigate - React Router navigate function
 */
export function loginAdvertiser(email, password, navigate) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast('Logging in...');
    try {
      const response = await apiConnector(LOGIN.type, LOGIN.url, {
        email,
        password,
      });

      console.log('Advertiser Login API response:', response);

      if (response.data.success) {
        // Check if MFA is required
        if (response.data.data.mfaRequired) {
          showSuccessToast('Please verify MFA code');
          // Store temp data for MFA verification
          sessionStorage.setItem('mfa_temp_id', response.data.data.user.id);
          navigate('/verify-mfa');
        } else {
          showSuccessToast('Login Successful!');
          
          // Extract user data and token from actual API response structure
          const userData = response.data.data.user;
          const accessToken = response.data.data.accessToken;
          
          const temp = {
            id: userData.id,
            uname: userData.name,
            uemail: userData.email,
            token: accessToken,
            mobile: userData.mobile,
            companyName: userData.companyName,
            hqLocation: userData.hqLocation,
            companySize: userData.companySize,
            role_id: 2,
            role: userData.role || 'advertiser',
            emailVerified: userData.emailVerifiedAt !== null,
            mfaEnabled: userData.mfaEnabled || false,
            status: userData.status,
          };
          
          dispatch(setAccount(temp));
          dispatch(
            setDFeature({
              dashboardFeature: 'Home',
            }),
          );
          navigate('/dashboard');
        }
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Advertiser Login API Error:', error);
      showValidationErrors(error);
    }
    toast.dismiss(loadingToast);
  };
}

/**
 * Resend verification email
 * @param {string} email - Advertiser's email
 */
export function resendVerificationEmail(email) {
  return async (dispatch) => {
    const toastId = showLoadingToast('Sending verification email...');
    try {
      const response = await apiConnector(
        RESEND_VERIFICATION.type,
        RESEND_VERIFICATION.url,
        { email },
      );

      console.log('Resend Verification API response:', response);

      if (response.data.success) {
        showSuccessToast('Verification email sent! Please check your inbox.');
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Resend Verification API Error:', error);
      showValidationErrors(error);
    }
    toast.dismiss(toastId);
  };
}

/**
 * Get advertiser profile
 * @param {string} token - Auth token
 */
export function getAdvertiserProfile(token) {
  return async (dispatch) => {
    try {
      const response = await apiConnector(
        PROFILE.type,
        PROFILE.url,
        {},
        {
          Authorization: `Bearer ${token}`,
        },
      );

      console.log('Get Profile API response:', response);

      if (response.data.success) {
        return response.data.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Get Profile API Error:', error);
      showValidationErrors(error);
      throw error;
    }
  };
}

/**
 * Verify MFA code during login
 * @param {string} advertiserId - Advertiser ID (from session storage)
 * @param {string} code - MFA code from authenticator app
 * @param {Function} navigate - React Router navigate function
 */
export function verifyMFA(advertiserId, code, navigate) {
  return async (dispatch) => {
    const toastId = showLoadingToast('Verifying MFA code...');
    try {
      const response = await apiConnector(VERIFY_MFA.type, VERIFY_MFA.url, {
        advertiserId,
        code,
      });

      console.log('Verify MFA API response:', response);

      if (response.data.success) {
        showSuccessToast('MFA verification successful!');
        
        const temp = {
          id: response.data.data.advertiserId,
          uname: response.data.data.name,
          uemail: response.data.data.email,
          token: response.data.data.token,
          role_id: 2, // Advertiser role
          role: 'advertiser',
          is_new: response.data.data.isNew,
        };
        
        dispatch(setAccount(temp));
        dispatch(
          setDFeature({
            dashboardFeature: 'Home',
          }),
        );
        
        // Clear session storage
        sessionStorage.removeItem('mfa_temp_id');
        
        navigate('/dashboard');
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Verify MFA API Error:', error);
      showValidationErrors(error);
    }
    toast.dismiss(toastId);
  };
}

/**
 * Toggle MFA (enable or disable)
 * @param {string} advertiserId - Advertiser ID
 * @param {boolean} enable - True to enable, false to disable
 * @param {string} token - Auth token
 */
export function toggleMFA(advertiserId, enable, token) {
  return async (dispatch, getState) => {
    const toastId = showLoadingToast(
      enable ? 'Enabling MFA...' : 'Disabling MFA...',
    );
    try {
      const response = await apiConnector(
        TOGGLE_MFA.type,
        TOGGLE_MFA.url,
        {
          advertiserId,
          enable,
        },
        {
          Authorization: `Bearer ${token}`,
        },
      );

      console.log('Toggle MFA API response:', response);

      if (response.data.success) {
        showSuccessToast(
          enable
            ? 'MFA enabled successfully! Scan the QR code with your authenticator app.'
            : 'MFA disabled successfully!',
        );
        
        // Get current user state and update only mfaEnabled
        const currentUser = getState().dashboard.account;
        const updatedAccount = {
          ...currentUser,
          mfaEnabled: enable,
        };
        dispatch(setAccount(updatedAccount));
        
        return response.data.data; // Returns QR code data if enabling
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Toggle MFA API Error:', error);
      showValidationErrors(error);
      return null;
    } finally {
      toast.dismiss(toastId);
    }
  };
}

/**
 * Update advertiser profile
 * @param {Object} profileData - Updated profile data (name, mobile, companyName, hqLocation, companySize)
 * @param {string} token - Auth token
 */
export function updateAdvertiserProfile(profileData, token) {
  return async (dispatch) => {
    const toastId = showLoadingToast('Updating profile...');
    try {
      const response = await apiConnector(
        UPDATE_PROFILE.type,
        UPDATE_PROFILE.url,
        profileData,
        {
          Authorization: `Bearer ${token}`,
        },
      );

      console.log('Update Profile API response:', response);

      if (response.data.success) {
        showSuccessToast('Profile updated successfully!');
        
        // Update Redux store with new profile data
        const updatedData = response.data.data.advertiser || response.data.data;
        const temp = {
          id: updatedData.id,
          uname: updatedData.name,
          uemail: updatedData.email,
          token: token,
          mobile: updatedData.mobile,
          companyName: updatedData.companyName,
          hqLocation: updatedData.hqLocation,
          companySize: updatedData.companySize,
          role_id: 2,
          role: 'advertiser',
          emailVerified: updatedData.emailVerified,
          mfaEnabled: updatedData.mfaEnabled,
        };
        
        dispatch(setAccount(temp));
        return true;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Update Profile API Error:', error);
      showValidationErrors(error);
      return false;
    } finally {
      toast.dismiss(toastId);
    }
  };
}

/**
 * Request password reset - sends email with reset link
 * @param {string} email - User's email
 */
export function requestPasswordReset(email) {
  return async () => {
    const toastId = showLoadingToast('Sending password reset email...');
    try {
      const response = await apiConnector(
        FORGOT_PASSWORD.type,
        FORGOT_PASSWORD.url,
        { email },
      );

      console.log('Request Password Reset API response:', response);

      if (response.data.success) {
        showSuccessToast('Password reset email sent! Please check your inbox.');
        return true;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Request Password Reset API Error:', error);
      showValidationErrors(error);
      return false;
    } finally {
      toast.dismiss(toastId);
    }
  };
}

/**
 * Validate password reset token
 * @param {string} token - Reset token from email
 * @param {string} email - User's email
 */
export function validateResetToken(token, email) {
  return async () => {
    const toastId = showLoadingToast('Validating reset token...');
    try {
      const response = await apiConnector(
        VALIDATE_RESET_TOKEN.type,
        `${VALIDATE_RESET_TOKEN.url}?token=${encodeURIComponent(token)}&email=${encodeURIComponent(email)}`,
      );

      console.log('Validate Reset Token API response:', response);

      if (response.data.success) {
        showSuccessToast('Token is valid. You can now reset your password.');
        return true;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Validate Reset Token API Error:', error);
      showValidationErrors(error);
      return false;
    } finally {
      toast.dismiss(toastId);
    }
  };
}

/**
 * Reset password with valid token
 * @param {string} token - Reset token from email
 * @param {string} email - User's email
 * @param {string} newPassword - New password
 * @param {Function} navigate - React Router navigate function
 */
export function resetPassword(token, email, newPassword, navigate) {
  return async () => {
    const toastId = showLoadingToast('Resetting password...');
    try {
      const response = await apiConnector(
        RESET_PASSWORD.type,
        `${RESET_PASSWORD.url}?token=${encodeURIComponent(token)}&email=${encodeURIComponent(email)}`,
        { newPassword },
      );

      console.log('Reset Password API response:', response);

      if (response.data.success) {
        showSuccessToast('Password reset successfully! Please login with your new password.');
        setTimeout(() => {
          navigate('/advertiser/login');
        }, 2000);
        return true;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Reset Password API Error:', error);
      showValidationErrors(error);
      return false;
    } finally {
      toast.dismiss(toastId);
    }
  };
}

/**
 * Change password for authenticated users
 * @param {string} oldPassword - Current password
 * @param {string} newPassword - New password
 * @param {string} token - Auth token
 */
export function changePassword(oldPassword, newPassword, token) {
  return async () => {
    const toastId = showLoadingToast('Changing password...');
    try {
      const response = await apiConnector(
        'PUT',
        `${authAdvertiserEndpoints.PROFILE.url}/change-password`,
        {
          oldPassword,
          newPassword,
        },
        {
          Authorization: `Bearer ${token}`,
        },
      );

      console.log('Change Password API response:', response);

      if (response.data.success) {
        showSuccessToast('Password changed successfully!');
        return true;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Change Password API Error:', error);
      showValidationErrors(error);
      return false;
    } finally {
      toast.dismiss(toastId);
    }
  };
}
