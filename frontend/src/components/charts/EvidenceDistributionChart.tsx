import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface EvidenceDistributionProps {
  data: Array<{
    level: number;
    count: number;
    label: string;
  }>;
}

export function EvidenceDistributionChart({ data }: EvidenceDistributionProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="label" />
        <YAxis label="干预措施数量" />
        <Tooltip />
        <Legend />
        <Bar dataKey="count" fill="#3b82f6" />
      </BarChart>
    </ResponsiveContainer>
  );
}
