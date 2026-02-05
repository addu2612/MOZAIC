//All the API endpoints will be declared here and then this will be used in entire frontend to access the endpoints...
const BaseURL = import.meta.env.VITE_API_BASE_URL;

// Authentication Endpoints
export const authAdvertiserEndpoints = {
  SIGNUP: { type: "POST", url: BaseURL + '/auth/advertiser/signup' },
  LOGIN: { type: "POST", url: BaseURL + '/auth/advertiser/login' },
  VERIFY_EMAIL: { type: "GET", url: BaseURL + '/auth/advertiser/verify' },
  RESEND_VERIFICATION: { type: "POST", url: BaseURL + '/auth/advertiser/resendVerification' },
  PROFILE: { type: "GET", url: BaseURL + '/auth/advertiser/profile' },
  VERIFY_MFA: { type: "POST", url: BaseURL + '/auth/advertiser/verify-mfa' },
  TOGGLE_MFA: { type: "POST", url: BaseURL + '/auth/advertiser/toggle-mfa' },
  UPDATE_PROFILE: { type: "PUT", url: BaseURL + '/auth/advertiser/profile' },
  FORGOT_PASSWORD: { type: "POST", url: BaseURL + '/auth/advertiser/forgot-password' },
  VALIDATE_RESET_TOKEN: { type: "GET", url: BaseURL + '/auth/advertiser/reset-password/validate' },
  RESET_PASSWORD: { type: "POST", url: BaseURL + '/auth/advertiser/reset-password' },
};

export const authPublisherEndpoints = {
  SIGNUP: { type: "POST", url: BaseURL + '/auth/publisher/signup' },
  LOGIN: { type: "POST", url: BaseURL + '/auth/publisher/login' },
  VERIFY_EMAIL: { type: "GET", url: BaseURL + '/auth/publisher/verify' },
  RESEND_VERIFICATION: { type: "POST", url: BaseURL + '/auth/publisher/resendVerification' },
  PROFILE: { type: "GET", url: BaseURL + '/auth/publisher/profile' },
  VERIFY_MFA: { type: "POST", url: BaseURL + '/auth/publisher/verify-mfa' },
  TOGGLE_MFA: { type: "POST", url: BaseURL + '/auth/publisher/toggle-mfa' },
  FORGOT_PASSWORD: { type: "POST", url: BaseURL + '/auth/publisher/forgot-password' },
  VALIDATE_RESET_TOKEN: { type: "GET", url: BaseURL + '/auth/publisher/reset-password/validate' },
  RESET_PASSWORD: { type: "POST", url: BaseURL + '/auth/publisher/reset-password' },
};

export const authClientEndpoints = {
  LOGIN: { type: "POST", url: BaseURL + '/auth/client/login' },
  PROFILE: { type: "GET", url: BaseURL + '/auth/client/profile' },
  VERIFY_MFA: { type: "POST", url: BaseURL + '/auth/client/verify-mfa' },
  TOGGLE_MFA: { type: "POST", url: BaseURL + '/auth/client/toggle-mfa' },
};

export const authAdminEndpoints = {
  LOGIN: { type: "POST", url: BaseURL + '/auth/admin/login' },
  PROFILE: { type: "GET", url: BaseURL + '/auth/admin/profile' },
  VERIFY_MFA: { type: "POST", url: BaseURL + '/auth/admin/verify-mfa' },
  TOGGLE_MFA: { type: "POST", url: BaseURL + '/auth/admin/toggle-mfa' },
};

// Publisher Endpoints
export const publisherEndpoints = {
  GET_PROFILE: { type: "GET", url: BaseURL + '/publishers/profile' },
  GET_ALL_TIERS: { type: "GET", url: BaseURL + '/publishers/tiers' },
  GET_CURRENT_TIER: { type: "GET", url: BaseURL + '/publishers/tier' },
};

export const publisherWebsiteEndpoints = {
  CREATE_WEBSITE: { type: "POST", url: BaseURL + '/publishers/websites' },
  GET_WEBSITES: { type: "GET", url: BaseURL + '/publishers/websites/{id}' },
  GET_WEBSITE_BY_ID_OR_URL: { type: "GET", url: BaseURL + '/publishers/websites/{publisherId}/{data}' },
  ACTIVATE_WEBSITE: { type: "GET", url: BaseURL + '/publishers/websites/activate/{publisherId}/{websiteId}' },
  DELETE_WEBSITE: { type: "DELETE", url: BaseURL + '/publishers/websites/{publisherId}/{websiteId}' },
};

export const publisherFloorPriceEndpoints = {
  CREATE_FLOOR_PRICE: { type: "POST", url: BaseURL + '/publishers/floorprice' },
  UPDATE_FLOOR_PRICE: { type: "PUT", url: BaseURL + '/publishers/floorprice' },
  GET_FLOOR_PRICES: { type: "GET", url: BaseURL + '/publishers/floorprice/{publisherId}/{adSlotId}' },
  GET_SINGLE_FLOOR_PRICE: { type: "GET", url: BaseURL + '/publishers/floorprice/{publisherId}/{adSlotId}/{floorPriceId}' },
  DELETE_FLOOR_PRICE: { type: "DELETE", url: BaseURL + '/publishers/floorprice/{publisherId}/{floorPriceId}' },
};

export const publisherAdInventoryEndpoints = {
  CREATE_AD_INVENTORY: { type: "POST", url: BaseURL + '/publishers/{publisherId}/websites/{websiteId}/adslots' },
  GET_AD_INVENTORY_LIST: { type: "GET", url: BaseURL + '/publishers/{publisherId}/websites/{websiteId}/adslots' },
  GET_AD_INVENTORY: { type: "GET", url: BaseURL + '/publishers/{publisherId}/websites/{websiteId}/adslots/{adSlotId}' },
  UPDATE_AD_INVENTORY: { type: "PATCH", url: BaseURL + '/publishers/{publisherId}/websites/{websiteId}/adslots/{adSlotId}' },
  DELETE_AD_INVENTORY: { type: "DELETE", url: BaseURL + '/publishers/{publisherId}/websites/{websiteId}/adslots/{adSlotId}' },
  TOGGLE_AD_INVENTORY_STATUS: { type: "PATCH", url: BaseURL + '/publishers/{publisherId}/websites/{websiteId}/adslots/{adSlotId}/toggle' },
};

export const publisherTargetingEndpoints = {
  ADD_DEMOGRAPHIC_TARGETING: { type: "POST", url: BaseURL + '/publishers' },
  GET_DEMOGRAPHIC_TARGETING: { type: "GET", url: BaseURL + '/publishers' },
  UPDATE_DEMOGRAPHIC_TARGETING: { type: "PUT", url: BaseURL + '/publishers' },
  DELETE_DEMOGRAPHIC_TARGETING: { type: "DELETE", url: BaseURL + '/publishers' },
  ADD_GEOGRAPHIC_TARGETING: { type: "POST", url: BaseURL + '/publishers' },
  GET_GEOGRAPHIC_TARGETING: { type: "GET", url: BaseURL + '/publishers' },
  UPDATE_GEOGRAPHIC_TARGETING: { type: "PUT", url: BaseURL + '/publishers' },
  DELETE_GEOGRAPHIC_TARGETING: { type: "DELETE", url: BaseURL + '/publishers' },
  ADD_DEVICE_TARGETING: { type: "POST", url: BaseURL + '/publishers' },
  GET_DEVICE_TARGETING: { type: "GET", url: BaseURL + '/publishers' },
  UPDATE_DEVICE_TARGETING: { type: "PUT", url: BaseURL + '/publishers' },
  DELETE_DEVICE_TARGETING: { type: "DELETE", url: BaseURL + '/publishers' },
  ADD_CONTEXTUAL_TARGETING: { type: "POST", url: BaseURL + '/publishers' },
  GET_CONTEXTUAL_TARGETING: { type: "GET", url: BaseURL + '/publishers' },
  UPDATE_CONTEXTUAL_TARGETING: { type: "PUT", url: BaseURL + '/publishers' },
  DELETE_CONTEXTUAL_TARGETING: { type: "DELETE", url: BaseURL + '/publishers' },
  ADD_BEHAVIORAL_TARGETING: { type: "POST", url: BaseURL + '/publishers' },
  GET_BEHAVIORAL_TARGETING: { type: "GET", url: BaseURL + '/publishers' },
  UPDATE_BEHAVIORAL_TARGETING: { type: "PUT", url: BaseURL + '/publishers' },
  DELETE_BEHAVIORAL_TARGETING: { type: "DELETE", url: BaseURL + '/publishers' },
  ADD_TIME_TARGETING: { type: "POST", url: BaseURL + '/publishers' },
  GET_TIME_TARGETING: { type: "GET", url: BaseURL + '/publishers' },
  UPDATE_TIME_TARGETING: { type: "PUT", url: BaseURL + '/publishers' },
  DELETE_TIME_TARGETING: { type: "DELETE", url: BaseURL + '/publishers' },
  ADD_FREQUENCY_TARGETING: { type: "POST", url: BaseURL + '/publishers' },
  GET_FREQUENCY_TARGETING: { type: "GET", url: BaseURL + '/publishers' },
  UPDATE_FREQUENCY_TARGETING: { type: "PUT", url: BaseURL + '/publishers' },
  DELETE_FREQUENCY_TARGETING: { type: "DELETE", url: BaseURL + '/publishers' },
  GET_ALL_TARGETING_RULES: { type: "GET", url: BaseURL + '/publishers' },
};

// Advertiser Endpoints
export const advertiserEndpoints = {
  GET_PROFILE: { type: "GET", url: BaseURL + '/advertiser/profile' },
  GET_CAMPAIGN_COUNTS: { type: "GET", url: BaseURL + '/advertiser/campaigns/counts' },
  GET_CAMPAIGNS_BY_STATUS: { type: "GET", url: BaseURL + '/advertiser/campaigns/status' },
};

export const advertiserCampaignEndpoints = {
  CREATE_CAMPAIGN: { type: "POST", url: BaseURL + '/advertiser' },
  GET_ALL_CAMPAIGNS: { type: "GET", url: BaseURL + '/advertiser' },
  UPDATE_CAMPAIGN: { type: "PATCH", url: BaseURL + '/advertiser' },
  GET_CAMPAIGN: { type: "GET", url: BaseURL + '/advertiser' },
  DELETE_CAMPAIGN: { type: "DELETE", url: BaseURL + '/advertiser' },
};

export const advertiserCampaignBudgetEndpoints = {
  ASSIGN_BUDGET: { type: "POST", url: BaseURL + '/advertiser' },
  UPDATE_BUDGET: { type: "PATCH", url: BaseURL + '/advertiser' },
  GET_BUDGET: { type: "GET", url: BaseURL + '/advertiser' },
  GET_DAILY_SPENDING: { type: "GET", url: BaseURL + '/advertiser' },
};

export const advertiserClientEndpoints = {
  CREATE_CLIENT: { type: "POST", url: BaseURL + '/advertiser/client/create' },
  GET_ALL_CLIENTS: { type: "GET", url: BaseURL + '/advertiser/client/get-clients' },
  GET_CLIENT_BY_ID: { type: "GET", url: BaseURL + '/advertiser/client' },
  UPDATE_CLIENT: { type: "PATCH", url: BaseURL + '/advertiser/client' },
  ASSIGN_CAMPAIGNS: { type: "POST", url: BaseURL + '/advertiser/client' },
};

export const advertiserTargetingEndpoints = {
  ADD_DEMOGRAPHIC_TARGETING: { type: "POST", url: BaseURL + '/campaign' },
  GET_DEMOGRAPHIC_TARGETING: { type: "GET", url: BaseURL + '/campaign' },
  UPDATE_DEMOGRAPHIC_TARGETING: { type: "PUT", url: BaseURL + '/campaign' },
  DELETE_DEMOGRAPHIC_TARGETING: { type: "DELETE", url: BaseURL + '/campaign' },
  ADD_GEOGRAPHIC_TARGETING: { type: "POST", url: BaseURL + '/campaign' },
  GET_GEOGRAPHIC_TARGETING: { type: "GET", url: BaseURL + '/campaign' },
  UPDATE_GEOGRAPHIC_TARGETING: { type: "PUT", url: BaseURL + '/campaign' },
  DELETE_GEOGRAPHIC_TARGETING: { type: "DELETE", url: BaseURL + '/campaign' },
  ADD_DEVICE_TARGETING: { type: "POST", url: BaseURL + '/campaign' },
  GET_DEVICE_TARGETING: { type: "GET", url: BaseURL + '/campaign' },
  UPDATE_DEVICE_TARGETING: { type: "PUT", url: BaseURL + '/campaign' },
  DELETE_DEVICE_TARGETING: { type: "DELETE", url: BaseURL + '/campaign' },
  ADD_CONTEXTUAL_TARGETING: { type: "POST", url: BaseURL + '/campaign' },
  GET_CONTEXTUAL_TARGETING: { type: "GET", url: BaseURL + '/campaign' },
  UPDATE_CONTEXTUAL_TARGETING: { type: "PUT", url: BaseURL + '/campaign' },
  DELETE_CONTEXTUAL_TARGETING: { type: "DELETE", url: BaseURL + '/campaign' },
  ADD_BEHAVIORAL_TARGETING: { type: "POST", url: BaseURL + '/campaign' },
  GET_BEHAVIORAL_TARGETING: { type: "GET", url: BaseURL + '/campaign' },
  UPDATE_BEHAVIORAL_TARGETING: { type: "PUT", url: BaseURL + '/campaign' },
  DELETE_BEHAVIORAL_TARGETING: { type: "DELETE", url: BaseURL + '/campaign' },
  ADD_TIME_TARGETING: { type: "POST", url: BaseURL + '/campaign' },
  GET_TIME_TARGETING: { type: "GET", url: BaseURL + '/campaign' },
  UPDATE_TIME_TARGETING: { type: "PUT", url: BaseURL + '/campaign' },
  DELETE_TIME_TARGETING: { type: "DELETE", url: BaseURL + '/campaign' },
  ADD_FREQUENCY_TARGETING: { type: "POST", url: BaseURL + '/campaign' },
  GET_FREQUENCY_TARGETING: { type: "GET", url: BaseURL + '/campaign' },
  UPDATE_FREQUENCY_TARGETING: { type: "PUT", url: BaseURL + '/campaign' },
  DELETE_FREQUENCY_TARGETING: { type: "DELETE", url: BaseURL + '/campaign' },
  GET_ALL_TARGETING_RULES: { type: "GET", url: BaseURL + '/campaign' },
};

export const advertiserCreativeEndpoints = {
  GET_AD_SLOT_TEMPLATES: { type: "GET", url: BaseURL + '/advertiser' },
  ADD_CREATIVE: { type: "POST", url: BaseURL + '/advertiser' },
  GET_ALL_CREATIVES: { type: "GET", url: BaseURL + '/advertiser' },
  UPDATE_CREATIVE: { type: "PATCH", url: BaseURL + '/advertiser' },
  GET_CREATIVE: { type: "GET", url: BaseURL + '/advertiser' },
  DELETE_CREATIVE: { type: "DELETE", url: BaseURL + '/advertiser' },
};

// Client Endpoints
export const clientCampaignEndpoints = {
  GET_ASSIGNED_CAMPAIGNS: { type: "GET", url: BaseURL + '/client/campaigns/assigned' },
  GET_ASSIGNED_CAMPAIGN_BY_ID: { type: "GET", url: BaseURL + '/client/campaigns/assigned' },
  GET_CAMPAIGN_BUDGET: { type: "GET", url: BaseURL + '/client/campaigns/assigned' },
  GET_CAMPAIGNS_DASHBOARD: { type: "GET", url: BaseURL + '/client/campaigns/dashboard/summary' },
};

// Admin Endpoints
export const adminAdvertiserEndpoints = {
  GET_ALL_ADVERTISERS: { type: "GET", url: BaseURL + '/admin/advertisers' },
  GET_ALL_ACTIVE_ADVERTISERS: { type: "GET", url: BaseURL + '/admin/advertisers/active' },
  GET_PENDING_VERIFICATION: { type: "GET", url: BaseURL + '/admin/advertisers/pending-verification' },
  GET_ADVERTISER_BY_ID: { type: "GET", url: BaseURL + '/admin/advertisers' },
  DELETE_ADVERTISER: { type: "DELETE", url: BaseURL + '/admin/advertisers' },
  GET_ADVERTISER_CAMPAIGNS: { type: "GET", url: BaseURL + '/admin/advertisers' },
  GET_ADVERTISER_CLIENTS: { type: "GET", url: BaseURL + '/admin/advertisers' },
  GET_PROFILE_DETAILS: { type: "GET", url: BaseURL + '/admin/advertisers' },
  UPDATE_STATUS: { type: "PATCH", url: BaseURL + '/admin/advertisers' },
  VERIFY_EMAIL: { type: "PATCH", url: BaseURL + '/admin/advertisers/verify-email' },
  RESET_PASSWORD: { type: "PATCH", url: BaseURL + '/admin/advertisers' },
  DISABLE_MFA: { type: "PATCH", url: BaseURL + '/admin/advertisers' },
};

export const adminClientEndpoints = {
  GET_ALL_CLIENTS: { type: "GET", url: BaseURL + '/admin/clients' },
  GET_CLIENT_BY_ID: { type: "GET", url: BaseURL + '/admin/clients' },
  DELETE_CLIENT: { type: "DELETE", url: BaseURL + '/admin/clients' },
  ASSOCIATE_ADVERTISER: { type: "PUT", url: BaseURL + '/admin/clients' },
  REMOVE_ADVERTISER_ASSOCIATION: { type: "DELETE", url: BaseURL + '/admin/clients' },
  UPDATE_CLIENT_STATUS: { type: "PUT", url: BaseURL + '/admin/clients' },
};

export const adminAdSlotTemplateEndpoints = {
  CREATE_TEMPLATE: { type: "POST", url: BaseURL + '/api/admin/adslot-templates' },
  GET_ALL_TEMPLATES: { type: "GET", url: BaseURL + '/api/admin/adslot-templates' },
  GET_TEMPLATE_BY_ID: { type: "GET", url: BaseURL + '/api/admin/adslot-templates' },
  UPDATE_TEMPLATE: { type: "PATCH", url: BaseURL + '/api/admin/adslot-templates' },
  DELETE_TEMPLATE: { type: "DELETE", url: BaseURL + '/api/admin/adslot-templates' },
  TOGGLE_STATUS: { type: "PATCH", url: BaseURL + '/api/admin/adslot-templates' },
};

export const adminContentCategoryEndpoints = {
  CREATE_CATEGORY: { type: "POST", url: BaseURL + '/api/admin/content-categories' },
  GET_ALL_CATEGORIES: { type: "GET", url: BaseURL + '/api/admin/content-categories' },
  GET_CATEGORY_BY_ID: { type: "GET", url: BaseURL + '/api/admin/content-categories' },
  UPDATE_CATEGORY: { type: "PATCH", url: BaseURL + '/api/admin/content-categories' },
  DELETE_CATEGORY: { type: "DELETE", url: BaseURL + '/api/admin/content-categories' },
  TOGGLE_STATUS: { type: "PATCH", url: BaseURL + '/api/admin/content-categories' },
};

export const adminPublisherTierEndpoints = {
  CREATE_TIER: { type: "POST", url: BaseURL + '/admin/publisher-tier' },
  GET_ALL_TIERS: { type: "GET", url: BaseURL + '/admin/publisher-tier' },
  GET_TIER_BY_ID: { type: "GET", url: BaseURL + '/admin/publisher-tier' },
  UPDATE_TIER: { type: "PATCH", url: BaseURL + '/admin/publisher-tier' },
  DELETE_TIER: { type: "DELETE", url: BaseURL + '/admin/publisher-tier' },
  ASSIGN_TIER_TO_PUBLISHER: { type: "POST", url: BaseURL + '/admin/publisher-tier/assign' },
  UNASSIGN_TIER_FROM_PUBLISHER: { type: "POST", url: BaseURL + '/admin/publisher-tier/unassign' },
  GET_PUBLISHER_TIER: { type: "GET", url: BaseURL + '/admin/publisher-tier/publisher' },
  GET_PUBLISHERS_IN_TIER: { type: "GET", url: BaseURL + '/admin/publisher-tier/tier' },
  INITIALIZE_DEFAULT_TIERS: { type: "POST", url: BaseURL + '/admin/publisher-tier/initialize-default-tiers' },
};

// RTB Endpoints
export const rtbEndpoints = {
  BID_REQUEST: { type: "POST", url: BaseURL + '/rtb/bid-request' },
  GET_BID_RESPONSE: { type: "GET", url: BaseURL + '/rtb/bid-response' },
  GET_AUCTION_STATUS: { type: "GET", url: BaseURL + '/rtb/auction' },
};

// Financial Monitoring Endpoints
export const financialMonitoringEndpoints = {
  GET_DASHBOARD: { type: "GET", url: BaseURL + '/financial/dashboard' },
  GET_PUBLISHER_REVENUE_STATUS: { type: "GET", url: BaseURL + '/financial/jobs/publisher-revenue/status' },
  GET_ADVERTISER_SPENDING_STATUS: { type: "GET", url: BaseURL + '/financial/jobs/advertiser-spending/status' },
  GET_SYSTEM_REVENUE_STATUS: { type: "GET", url: BaseURL + '/financial/jobs/system-revenue/status' },
  TRIGGER_PUBLISHER_REVENUE_PROCESSING: { type: "POST", url: BaseURL + '/financial/jobs/publisher-revenue/trigger' },
  TRIGGER_ADVERTISER_SPENDING_PROCESSING: { type: "POST", url: BaseURL + '/financial/jobs/advertiser-spending/trigger' },
  TRIGGER_SYSTEM_REVENUE_PROCESSING: { type: "POST", url: BaseURL + '/financial/jobs/system-revenue/trigger' },
  TRIGGER_ALL_FINANCIAL_PROCESSING: { type: "POST", url: BaseURL + '/financial/jobs/all/trigger' },
  GET_REVENUE_INSIGHTS: { type: "GET", url: BaseURL + '/financial/insights/revenue' },
  GET_REVENUE_INSIGHTS_FOR_PERIOD: { type: "GET", url: BaseURL + '/financial/insights/revenue' },
  GET_CAMPAIGN_METRICS: { type: "GET", url: BaseURL + '/financial/campaign' },
  GET_CREATIVE_METRICS: { type: "GET", url: BaseURL + '/financial/creative' },
  GET_PUBLISHER_REVENUE: { type: "GET", url: BaseURL + '/financial/publisher' },
};

// Budget Sync Endpoints
export const budgetSyncEndpoints = {
  GET_BUDGET_SYNC_STATUS: { type: "GET", url: BaseURL + '/budget-sync/status' },
  TRIGGER_DAILY_SYNC: { type: "POST", url: BaseURL + '/budget-sync/trigger/daily' },
  TRIGGER_TOTAL_SYNC: { type: "POST", url: BaseURL + '/budget-sync/trigger/total' },
  TRIGGER_EMERGENCY_SYNC: { type: "POST", url: BaseURL + '/budget-sync/trigger/emergency' },
  SYNC_SPECIFIC_CAMPAIGN: { type: "POST", url: BaseURL + '/budget-sync/sync/campaign' },
  GET_BUDGET_SYNC_METRICS: { type: "GET", url: BaseURL + '/budget-sync/metrics' },
  GET_BUDGET_SYNC_HEALTH: { type: "GET", url: BaseURL + '/budget-sync/health' },
  COMPARE_BUDGET_DATA: { type: "GET", url: BaseURL + '/budget-sync/comparison' },
};