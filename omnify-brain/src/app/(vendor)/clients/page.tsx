'use client';

import { useState, useEffect } from 'react';
import { Building2, Users, DollarSign, Activity, Search, MoreVertical } from 'lucide-react';

interface Organization {
  id: string;
  name: string;
  plan: string;
  status: string;
  userCount: number;
  mrr: number;
  lastActive: string;
}

export default function VendorClientsPage() {
  const [clients, setClients] = useState<Organization[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState('all');

  // Mock data - replace with API call
  useEffect(() => {
    setClients([
      {
        id: '1',
        name: 'Demo Beauty Co',
        plan: 'Growth',
        status: 'active',
        userCount: 12,
        mrr: 299,
        lastActive: '2 hours ago',
      },
      {
        id: '2',
        name: 'Acme Fashion',
        plan: 'Enterprise',
        status: 'active',
        userCount: 45,
        mrr: 999,
        lastActive: '5 minutes ago',
      },
      {
        id: '3',
        name: 'TechStart Inc',
        plan: 'Starter',
        status: 'trialing',
        userCount: 3,
        mrr: 0,
        lastActive: '1 day ago',
      },
    ]);
  }, []);

  const filteredClients = clients.filter((client) => {
    const matchesSearch = client.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filter === 'all' || client.status === filter;
    return matchesSearch && matchesFilter;
  });

  const totalMRR = clients.reduce((sum, client) => sum + client.mrr, 0);
  const activeClients = clients.filter((c) => c.status === 'active').length;
  const totalUsers = clients.reduce((sum, client) => sum + client.userCount, 0);

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Client Management</h1>
        <p className="text-slate-400">Manage all client organizations</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-6 mb-8">
        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <div className="flex items-center gap-3 mb-2">
            <Building2 className="h-5 w-5 text-blue-400" />
            <p className="text-sm text-slate-400">Total Clients</p>
          </div>
          <p className="text-3xl font-bold">{clients.length}</p>
        </div>

        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <div className="flex items-center gap-3 mb-2">
            <Activity className="h-5 w-5 text-green-400" />
            <p className="text-sm text-slate-400">Active Clients</p>
          </div>
          <p className="text-3xl font-bold">{activeClients}</p>
        </div>

        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <div className="flex items-center gap-3 mb-2">
            <DollarSign className="h-5 w-5 text-amber-400" />
            <p className="text-sm text-slate-400">Monthly Revenue</p>
          </div>
          <p className="text-3xl font-bold">${totalMRR.toLocaleString()}</p>
        </div>

        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <div className="flex items-center gap-3 mb-2">
            <Users className="h-5 w-5 text-purple-400" />
            <p className="text-sm text-slate-400">Total Users</p>
          </div>
          <p className="text-3xl font-bold">{totalUsers}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 mb-6">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
            <input
              type="text"
              placeholder="Search clients..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="trialing">Trialing</option>
            <option value="past_due">Past Due</option>
            <option value="canceled">Canceled</option>
          </select>
        </div>
      </div>

      {/* Client List */}
      <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-900 border-b border-slate-700">
            <tr>
              <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Organization</th>
              <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Plan</th>
              <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Status</th>
              <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Users</th>
              <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">MRR</th>
              <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Last Active</th>
              <th className="text-right px-6 py-4 text-sm font-medium text-slate-400">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700">
            {filteredClients.map((client) => (
              <tr key={client.id} className="hover:bg-slate-700/50 transition-colors">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
                      <Building2 className="h-5 w-5 text-blue-400" />
                    </div>
                    <div>
                      <p className="font-medium">{client.name}</p>
                      <p className="text-sm text-slate-400">{client.id}</p>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className="px-3 py-1 bg-purple-500/20 text-purple-300 rounded-full text-sm font-medium">
                    {client.plan}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-medium ${
                      client.status === 'active'
                        ? 'bg-green-500/20 text-green-300'
                        : client.status === 'trialing'
                        ? 'bg-blue-500/20 text-blue-300'
                        : 'bg-red-500/20 text-red-300'
                    }`}
                  >
                    {client.status}
                  </span>
                </td>
                <td className="px-6 py-4 text-slate-300">{client.userCount}</td>
                <td className="px-6 py-4 font-medium">${client.mrr}</td>
                <td className="px-6 py-4 text-slate-400">{client.lastActive}</td>
                <td className="px-6 py-4 text-right">
                  <button className="p-2 hover:bg-slate-700 rounded-lg transition-colors">
                    <MoreVertical className="h-5 w-5 text-slate-400" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredClients.length === 0 && (
        <div className="text-center py-12 text-slate-400">
          No clients found matching your criteria
        </div>
      )}
    </div>
  );
}
