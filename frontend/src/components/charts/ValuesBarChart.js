import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const ValuesBarChart = ({ valuesData }) => {
  // 기본 데이터
  const defaultData = {
    creativity_innovation: 0.75,
    social_connection: 0.68,
    achievement_success: 0.58,
    harmony_stability: 0.41,
    authenticity_depth: 0.52
  };

  const data = {
    labels: [
      '창의성과 혁신',
      '사회적 연결',
      '성취와 성공',
      '조화와 안정',
      '진정성과 깊이'
    ],
    datasets: [
      {
        label: '가치관 점수',
        data: [
          valuesData?.creativity_innovation || defaultData.creativity_innovation,
          valuesData?.social_connection || defaultData.social_connection,
          valuesData?.achievement_success || defaultData.achievement_success,
          valuesData?.harmony_stability || defaultData.harmony_stability,
          valuesData?.authenticity_depth || defaultData.authenticity_depth,
        ],
        backgroundColor: [
          'rgba(229, 9, 20, 0.8)',
          'rgba(245, 197, 24, 0.8)',
          'rgba(70, 211, 105, 0.8)',
          'rgba(52, 152, 219, 0.8)',
          'rgba(155, 89, 182, 0.8)',
        ],
        borderColor: [
          'rgba(229, 9, 20, 1)',
          'rgba(245, 197, 24, 1)',
          'rgba(70, 211, 105, 1)',
          'rgba(52, 152, 219, 1)',
          'rgba(155, 89, 182, 1)',
        ],
        borderWidth: 2,
        borderRadius: 8,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#1a1a1a',
        titleColor: '#ffffff',
        bodyColor: '#ffffff',
        borderColor: '#e50914',
        borderWidth: 1,
        callbacks: {
          label: function(context) {
            const score = (context.parsed.y * 100).toFixed(0);
            return `${score}점`;
          },
        },
      },
    },
    scales: {
      x: {
        ticks: {
          color: '#ffffff',
          font: { size: 12 },
          maxRotation: 45,
        },
        grid: { display: false },
      },
      y: {
        beginAtZero: true,
        min: 0,
        max: 1,
        ticks: {
          color: '#a0a0a0',
          font: { size: 12 },
          callback: function(value) {
            return (value * 100).toFixed(0) + '점';
          },
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
      },
    },
    animation: {
      duration: 1000,
      easing: 'easeOutQuart',
    },
  };

  return (
    <div style={{
      width: '100%',
      height: '300px',
      position: 'relative'
    }}>
      <Bar data={data} options={options} />
    </div>
  );
};

export default ValuesBarChart;
