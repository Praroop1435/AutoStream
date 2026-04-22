"use client";

import React from 'react';
import { LayoutDashboard, MessageSquare, Database, Settings, Activity } from 'lucide-react';
import styles from './Sidebar.module.css';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onLogout: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, onLogout }) => {
  const menuItems = [
    { id: 'chat', label: 'AI Agent', icon: MessageSquare },
    { id: 'leads', label: 'Lead Dashboard', icon: LayoutDashboard },
    { id: 'knowledge', label: 'Knowledge Base', icon: Database },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className={styles.sidebar}>
      <div className={styles.logo}>
        <Activity className={styles.logoIcon} size={28} />
        <span>AutoStream</span>
      </div>

      <nav className={styles.nav}>
        {menuItems.map((item) => {
          const Icon = item.icon;
          return (
            <div
              key={item.id}
              className={`${styles.navItem} ${activeTab === item.id ? styles.active : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </div>
          );
        })}
      </nav>

      <div className={styles.footer}>
        <div className={styles.statusCard}>
          <div className={styles.statusIndicator} />
          <span>System Online</span>
        </div>
        <button className={styles.logoutButton} onClick={onLogout}>
          Sign Out
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
