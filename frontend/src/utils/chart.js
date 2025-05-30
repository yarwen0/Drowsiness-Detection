import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

export const createChartData = (earHistory, marHistory) => {
  const labels = Array.from({ length: earHistory.length }, (_, i) => i + 1);

  return {
    labels,
    datasets: [
      {
        label: 'Eye Aspect Ratio (EAR)',
        data: earHistory,
        borderColor: '#4a90e2',
        backgroundColor: 'rgba(74, 144, 226, 0.1)',
        tension: 0.4,
        fill: true,
      },
      {
        label: 'Mouth Aspect Ratio (MAR)',
        data: marHistory,
        borderColor: '#e74c3c',
        backgroundColor: 'rgba(231, 76, 60, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  };
};

export const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
      labels: {
        font: {
          size: 12,
        },
      },
    },
    tooltip: {
      mode: 'index',
      intersect: false,
    },
  },
  scales: {
    x: {
      grid: {
        display: false,
      },
      ticks: {
        maxTicksLimit: 10,
      },
    },
    y: {
      beginAtZero: true,
      grid: {
        color: 'rgba(0, 0, 0, 0.1)',
      },
    },
  },
  interaction: {
    mode: 'nearest',
    axis: 'x',
    intersect: false,
  },
  animation: {
    duration: 750,
    easing: 'easeInOutQuart',
  },
};

export const calculateStatistics = (earHistory, marHistory, drowsinessCount, blinkCount) => {
  const averageEAR = earHistory.length > 0
    ? earHistory.reduce((a, b) => a + b, 0) / earHistory.length
    : 0;

  const averageMAR = marHistory.length > 0
    ? marHistory.reduce((a, b) => a + b, 0) / marHistory.length
    : 0;

  const blinkRate = earHistory.length > 0
    ? (blinkCount / earHistory.length) * 100
    : 0;

  const drowsinessRate = earHistory.length > 0
    ? (drowsinessCount / earHistory.length) * 100
    : 0;

  return {
    averageEAR: averageEAR.toFixed(3),
    averageMAR: averageMAR.toFixed(3),
    blinkRate: blinkRate.toFixed(1),
    drowsinessRate: drowsinessRate.toFixed(1),
  };
};

export const formatNumber = (number) => {
  return Number(number).toLocaleString('en-US', {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  });
}; 