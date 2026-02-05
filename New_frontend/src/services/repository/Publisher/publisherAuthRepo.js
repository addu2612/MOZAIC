// Publisher Authentication Repository
// This repository handles all publisher authentication flows including registration, login, MFA, and password management
import { apiConnector } from '../../Connector.js';
import {
  setAccount,
  setAccountAfterRegister,
  setDFeature,
} from '../../../app/DashboardSlice.js';
import { authPublisherEndpoints } from '../../Apis.js';
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
  FORGOT_PASSWORD,
  VALIDATE_RESET_TOKEN,
  RESET_PASSWORD,
} = authPublisherEndpoints;


export function registerPublisher(
  firstName,
  lastName,
  email,
  password,
  domain,
  navigate,
) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast('Registering publisher...');
    try {
      const response = await apiConnector(SIGNUP.type, SIGNUP.url, {
        firstName,
        lastName,
        email,
        password,
        domain,
      });

      console.log('Publisher Registration API response:', response);

      if (response.data.success) {
        showSuccessToast('Registration Successful! Please verify your email.');
        
        // Extract publisher data from response
        const publisherData = response.data.data.publisher;
        
        const temp = {
          id: publisherData.id,
          uname: `${publisherData.firstName} ${publisherData.lastName}`,
          uemail: publisherData.email,
          domain: publisherData.domain,
          role: 'publisher',
          role_id: 3,
          emailVerified: false,
          mfaEnabled: publisherData.mfaEnabled || false,
          status: publisherData.status,
        };
        
        // Store email for resend verification
        localStorage.setItem('pending_verification_email', publisherData.email);
        
        dispatch(setAccountAfterRegister(temp));
        navigate('/publisher/verify-email');
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      console.log('Publisher Registration API Error:', error);
      showValidationErrors(error);
    }
    toast.dismiss(loadingToast);
  };
}

/**
 * Verify publisher email with token
 * @param {string} token - Verification token from email
 * @param {Function} navigate - React Router navigate function
 */
export function verifyPublisherEmail(token, navigate) {
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
        navigate('/publisher/login');
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
 * Login publisher
 * @param {string} email - Publisher's email
 * @param {string} password - Publisher's password
 * @param {Function} navigate - React Router navigate function
 */
export function loginPublisher(email, password, navigate) {
  return async (dispatch) => {
    const loadingToast = showLoadingToast('Logging in...');
    try {
      const response = await apiConnector(LOGIN.type, LOGIN.url, {
        email,
        password,
      });

      console.log('Publisher Login API response:', response);

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
            uname: `${userData.firstName} ${userData.lastName}`,
            uemail: userData.email,
            token: accessToken,
            role_id: 3,
            role: userData.role || 'publisher',
            emailVerified: userData.emailVerifiedAt !== null,
            mfaEnabled: userData.mfaEnabled || false,
            status: userData.status,
            paymentThreshold: userData.paymentThreshold,
            tierId: userData.tierId,
            tier: userData.tier,
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
      console.log('Publisher Login API Error:', error);
      showValidationErrors(error);
    }
    toast.dismiss(loadingToast);
  };
}

/**
 * Resend verification email
 * @param {string} email - Publisher's email
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
 * Get publisher profile
 * @param {string} token - Auth token
 */
export function getPublisherProfile(token) {
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
 * @param {string} publisherId - Publisher ID (from session storage)
 * @param {string} code - MFA code from authenticator app
 * @param {Function} navigate - React Router navigate function
 */
export function verifyMFA(publisherId, code, navigate) {
  return async (dispatch) => {
    const toastId = showLoadingToast('Verifying MFA code...');
    try {
      const response = await apiConnector(VERIFY_MFA.type, VERIFY_MFA.url, {
        publisherId,
        code,
      });

      console.log('Verify MFA API response:', response);

      if (response.data.success) {
        showSuccessToast('MFA verification successful!');
        
        const temp = {
          id: response.data.data.publisherId,
          uname: response.data.data.name,
          uemail: response.data.data.email,
          token: response.data.data.token,
          role_id: 3, // Publisher role
          role: 'publisher',
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
 * @param {string} publisherId - Publisher ID
 * @param {boolean} enable - True to enable, false to disable
 * @param {string} token - Auth token
 */
export function toggleMFA(publisherId, enable, token) {
  return async (dispatch, getState) => {
    const toastId = showLoadingToast(
      enable ? 'Enabling MFA...' : 'Disabling MFA...',
    );
    try {
      const response = await apiConnector(
        TOGGLE_MFA.type,
        TOGGLE_MFA.url,
        {
          publisherId,
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
          navigate('/publisher/login');
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