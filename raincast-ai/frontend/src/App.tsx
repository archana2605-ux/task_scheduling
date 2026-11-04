import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import OverviewPage from './pages/OverviewPage';
import LiveForecastPage from './pages/LiveForecastPage';
import InteractiveMapPage from './pages/InteractiveMapPage';
import LocationForecastPage from './pages/LocationForecastPage';
import ModelComparisonPage from './pages/ModelComparisonPage';
import AnalyticsPage from './pages/AnalyticsPage';
import VerificationPage from './pages/VerificationPage';
import DataSourcesPage from './pages/DataSourcesPage';
import AboutPage from './pages/AboutPage';
import type { ForecastModel } from './types';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000,
    },
  },
});

function AppContent() {
  const [model, setModel] = useState<ForecastModel>('ifs');

  return (
    <div className="flex h-screen overflow-hidden bg-navy-950">
      {/* Sidebar */}
      <Sidebar model={model} onModelChange={setModel} />

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header model={model} />
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<OverviewPage model={model} />} />
            <Route path="/forecast" element={<LiveForecastPage model={model} />} />
            <Route path="/map" element={<InteractiveMapPage model={model} />} />
            <Route path="/location" element={<LocationForecastPage model={model} />} />
            <Route path="/comparison" element={<ModelComparisonPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/verification" element={<VerificationPage />} />
            <Route path="/data-sources" element={<DataSourcesPage />} />
            <Route path="/about" element={<AboutPage />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
