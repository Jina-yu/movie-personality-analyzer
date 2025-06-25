import React from 'react';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';
import { Radar } from 'react-chartjs-2';

// Chart.js 컴포넌트 등록
ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

const PersonalityRadarChart = ({ personalityData, size = 400 }) => {
  // 기본 데이터 (personalityData가 없을 때 대비)
  const defaultData = {
    openness: 0.7,
    conscientiousness: 0.5,
    extraversion: 0.8,
    agreeableness: 0.6,
    neuroticism: 0.3
  };

  const data = {
    labels: ['개방성', '성실성', '외향성', '친화성', '신경성'],
    datasets: [
      {
        label: '성격 특성 점수',
        data: [
          personalityData?.openness || defaultData.openness,
          personalityData?.conscientiousness || defaultData.conscientiousness,
          personalityData?.extraversion || defaultData.extraversion,
          personalityData?.agreeableness || defaultData.agreeableness,
          personalityData?.neuroticism || defaultData.neuroticism,
        ],
        backgroundColor: 'rgba(229, 9, 20, 0.2)',
        borderColor: 'rgba(229, 9, 20, 1)',
        borderWidth: 3,
        pointBackgroundColor: 'rgba(229, 9, 20, 1)',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 6,
        fill: true,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: '#ffffff',
          font: { size: 14 },
        },
      },
      tooltip: {
        backgroundColor: '#1a1a1a',
        titleColor: '#ffffff',
        bodyColor: '#ffffff',
        borderColor: '#e50914',
        borderWidth: 1,
        callbacks: {
          label: function(context) {
            const score = (context.parsed.r * 100).toFixed(0);
            return `${context.dataset.label}: ${score}점`;
          },
        },
      },
    },
    scales: {
      r: {
        beginAtZero: true,
        min: 0,
        max: 1,
        ticks: {
          stepSize: 0.2,
          color: '#a0a0a0',
          font: { size: 12 },
          callback: function(value) {
            return (value * 100).toFixed(0) + '점';
          },
        },
        pointLabels: {
          color: '#ffffff',
          font: { size: 14, weight: '600' },
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        angleLines: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
      },
    },
    animation: {
      duration: 1500,
      easing: 'easeInOutQuart',
    },
  };

  return (
    <div style={{
      width: '100%',
      height: `${size}px`,
      position: 'relative'
    }}>
      <Radar data={data} options={options} />
    </div>
  );
};

export default PersonalityRadarChart;
