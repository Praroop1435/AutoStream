"use client";

import React, { useEffect, useState } from 'react';
import { Users, DollarSign, TrendingUp, Clock } from 'lucide-react';

interface Lead {
  id: number;
  name: string;
  email: string;
  platform: string;
  created_at: string;
}

const LeadDashboard: React.FC = () => {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchLeads = async () => {
      try {
        const token = localStorage.getItem('auth_token');
        const response = await fetch("http://localhost:8000/leads", {
          headers: { "Authorization": `Bearer ${token}` }
        });
        if (response.ok) {
          const data = await response.json();
          setLeads(data.leads || []);
        }
      } catch (error) {
        console.error("Failed to fetch leads", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchLeads();
  }, []);

  const totalLeads = leads.length;
  const revenuePipeline = totalLeads * 50; // Dummy calculation for now based on $50 per lead
  
  const stats = [
    { label: 'Total Leads', value: totalLeads.toString(), icon: Users, color: '#6366f1' },
    { label: 'Revenue Pipeline', value: `$${revenuePipeline.toLocaleString()}`, icon: DollarSign, color: '#10b981' },
    { label: 'Conversion Rate', value: '0%', icon: TrendingUp, color: '#22d3ee' },
    { label: 'Avg. Response', value: 'N/A', icon: Clock, color: '#f59e0b' },
  ];

  if (isLoading) {
    return <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>Loading dashboard...</div>;
  }

  return (
    <div style={{ flex: 1, padding: '40px', overflowY: 'auto' }}>
      <h1 style={{ fontSize: '28px', fontWeight: '700', marginBottom: '32px' }}>Lead Dashboard</h1>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '24px', marginBottom: '48px' }}>
        {stats.map((stat, i) => (
          <div key={i} style={{ 
            backgroundColor: 'var(--card-bg)', 
            border: '1px solid var(--border)', 
            padding: '24px', 
            borderRadius: '16px',
            backdropFilter: 'var(--glass)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <span style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>{stat.label}</span>
              <stat.icon size={20} color={stat.color} />
            </div>
            <div style={{ fontSize: '24px', fontWeight: '700' }}>{stat.value}</div>
          </div>
        ))}
      </div>

      <div style={{ backgroundColor: 'var(--card-bg)', border: '1px solid var(--border)', borderRadius: '16px', overflow: 'hidden' }}>
        <div style={{ padding: '24px', borderBottom: '1px solid var(--border)', fontWeight: '600' }}>Recent Leads</div>
        {leads.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>No leads captured yet.</div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ color: 'var(--text-secondary)', fontSize: '13px', borderBottom: '1px solid var(--border)' }}>
                <th style={{ padding: '16px 24px' }}>Name</th>
                <th style={{ padding: '16px 24px' }}>Interest (Platform)</th>
                <th style={{ padding: '16px 24px' }}>Email</th>
                <th style={{ padding: '16px 24px' }}>Date</th>
              </tr>
            </thead>
            <tbody>
              {leads.map((lead) => (
                <tr key={lead.id} style={{ borderBottom: '1px solid var(--border)', fontSize: '14px' }}>
                  <td style={{ padding: '16px 24px', fontWeight: '500' }}>{lead.name}</td>
                  <td style={{ padding: '16px 24px' }}>{lead.platform}</td>
                  <td style={{ padding: '16px 24px' }}>{lead.email}</td>
                  <td style={{ padding: '16px 24px', color: 'var(--text-secondary)' }}>
                    {new Date(lead.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default LeadDashboard;
