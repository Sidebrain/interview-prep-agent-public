import React from 'react';
import { LineChart, XAxis, YAxis, Tooltip, Legend, Line } from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

const EvaluationResults = ({ evaluations }) => {
  // Transform evaluation data for visualization
  const chartData = evaluations.map(eval => ({
    metric: eval.name,
    score: eval.score * 100,
    confidence: eval.confidence * 100
  }));

  return (
    <Card className="w-full max-w-4xl">
      <CardHeader>
        <CardTitle>Evaluation Results</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-64">
          <LineChart width={600} height={200} data={chartData}>
            <XAxis dataKey="metric" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="score" stroke="#8884d8" />
            <Line type="monotone" dataKey="confidence" stroke="#82ca9d" />
          </LineChart>
        </div>
        
        <div className="mt-4 grid grid-cols-3 gap-4">
          {chartData.map(item => (
            <div 
              key={item.metric} 
              className="p-4 border rounded-lg bg-white"
            >
              <h3 className="font-medium text-gray-900">{item.metric}</h3>
              <p className="text-2xl font-bold text-blue-600">
                {item.score.toFixed(1)}%
              </p>
              <p className="text-sm text-gray-500">
                Confidence: {item.confidence.toFixed(1)}%
              </p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default EvaluationResults;