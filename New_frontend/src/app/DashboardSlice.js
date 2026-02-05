import { createSlice } from '@reduxjs/toolkit';

// Safely parse localStorage data
const getLocalStorageItem = (key) => {
  try {
    const item = localStorage.getItem(key);
    return item && item !== 'undefined' && item !== 'null' ? JSON.parse(item) : null;
  } catch (error) {
    console.error(`Error parsing localStorage key "${key}":`, error);
    return null;
  }
};

const localData = getLocalStorageItem('account');
const Dstate = getLocalStorageItem('dState');

const initialState = {
  dashboardMenuState: true,
  dashboardFeature: Dstate || 'dashboard',
  account: localData || null,
  isLoggedIn: localData?.isLoggedIn ?? false,
  profileData: [],
  dashboardData: {
    welcome: {
      temperature: 28,
      weather: 'Sunny Day',
      weatherDescription: 'Beautiful Day',
    },
    // Adtech-specific metrics will be populated from API
    campaigns: {
      total: 0,
      active: 0,
      paused: 0,
      completed: 0,
    },
    budget: {
      totalSpent: 0,
      totalBudget: 0,
      dailySpent: 0,
      dailyBudget: 0,
    },
    performance: {
      impressions: 0,
      clicks: 0,
      conversions: 0,
      ctr: 0,
    },
  },
};

const DashboardSlice = createSlice({
  initialState,
  name: 'dashboard',
  reducers: {
    setOpenDMenu: (state, action) => {
      state.dashboardMenuState = action.payload.dashboardMenuState;
    },
    setCloseDMenu: (state, action) => {
      state.dashboardMenuState = action.payload.dashboardMenuState;
    },
    setDFeature: (state, action) => {
      state.dashboardFeature = action.payload.dashboardFeature;
      localStorage.setItem(
        'dState',
        JSON.stringify(action.payload.dashboardFeature),
      );
    },
    setAccount: (state, action) => {
      state.account = action.payload;
      state.isLoggedIn = true;
      const temp = { ...state.account, isLoggedIn: state.isLoggedIn };
      localStorage.setItem('account', JSON.stringify(temp));
    },
    LogOut: (state, action) => {
      state.account = [];
      state.profileData = [];
      state.isLoggedIn = false;
      state.dashboardMenuState = false;
      state.dashboardFeature = 'dashboard';
      localStorage.clear();
    },
    setAccountAfterRegister: (state, action) => {
      state.account = action.payload;
      state.isLoggedIn = false;
      const temp1 = { ...state.account, isLoggedIn: state.isLoggedIn };
      localStorage.setItem('account', JSON.stringify(temp1));
    },
  },
});

export const {
  setOpenDMenu,
  setCloseDMenu,
  setDFeature,
  setAccount,
  setAccountAfterRegister,
  LogOut,
} = DashboardSlice.actions;

export const dashboardMenuState = (state) => state.dashboard.dashboardMenuState;
export const dashboardFeature = (state) => state.dashboard.dashboardFeature;
export const isUserLoggedIn = (state) => state.dashboard.isLoggedIn;
export const selectAccount = (state) => state.dashboard.account;
export const selectProfileData = (state) => state.dashboard.profileData;
export const selectDashboardData = (state) => state.dashboard.dashboardData;

export default DashboardSlice.reducer;
