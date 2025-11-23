import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent, Table, TableHeader, TableBody, TableRow, TableHead, TableCell, Badge, Input, Button } from '@omnify/shared-ui';
import { Search, Mail, Building } from 'lucide-react';

const UserManagement = () => {
  const [search, setSearch] = useState('');

  const users = [
    { id: 'user1', name: 'Sarah Johnson', email: 'sarah@example.com', company: 'DTC Brand', plan: 'Professional', status: 'active' },
    { id: 'user2', name: 'Marcus Chen', email: 'marcus@example.com', company: 'SaaS Co', plan: 'Professional', status: 'active' },
    { id: 'user3', name: 'Jennifer Smith', email: 'jennifer@example.com', company: 'B2B Enterprise', plan: 'Enterprise', status: 'active' },
    { id: 'user4', name: 'David Lee', email: 'david@example.com', company: 'E-commerce', plan: 'Starter', status: 'inactive' }
  ];

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">User Management</h1>
        <p className="text-gray-600">Manage user accounts and subscriptions</p>
      </div>

      <Card className="mb-6">
        <CardContent className="p-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input 
              placeholder="Search users..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>All Users</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Company</TableHead>
                <TableHead>Plan</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell className="font-medium">{user.name}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>{user.company}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{user.plan}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={user.status === 'active' ? 'default' : 'secondary'}>
                      {user.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Button variant="outline" size="sm">View</Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

export default UserManagement;


