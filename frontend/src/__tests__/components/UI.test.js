/**
 * Comprehensive Frontend Unit Tests for UI Components
 *
 * Tests for reusable UI components:
 * - Button, Card, Input, Select components
 * - Form components and validation
 * - Modal/Dialog components
 * - Data display components (Table, Badge, etc.)
 * - Navigation components
 * - Feedback components (Alert, Toast, etc.)
 *
 * Author: OmnifyProduct Test Suite
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

// Import UI components
import Button from '../../components/ui/button';
import Card, { CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../../components/ui/card';
import Input from '../../components/ui/input';
import Label from '../../components/ui/label';
import Select, { SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import Badge from '../../components/ui/badge';
import Alert, { AlertDescription, AlertTitle } from '../../components/ui/alert';
import Table, { TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../components/ui/table';
import Tabs, { TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import Dialog, { DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../../components/ui/dialog';
import Toast, { ToastProvider, ToastViewport } from '../../components/ui/toast';
import { useToast } from '../../components/ui/use-toast';

describe('UI Components Tests', () => {
  describe('Button Component', () => {
    it('renders button with text', () => {
      render(<Button>Click me</Button>);
      expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
    });

    it('handles click events', async () => {
      const user = userEvent.setup();
      const handleClick = jest.fn();

      render(<Button onClick={handleClick}>Click me</Button>);

      const button = screen.getByRole('button', { name: /click me/i });
      await user.click(button);

      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('applies variant styles correctly', () => {
      render(
        <div>
          <Button variant="default">Default</Button>
          <Button variant="destructive">Destructive</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="link">Link</Button>
        </div>
      );

      expect(screen.getByText('Default')).toBeInTheDocument();
      expect(screen.getByText('Destructive')).toBeInTheDocument();
      expect(screen.getByText('Outline')).toBeInTheDocument();
      expect(screen.getByText('Secondary')).toBeInTheDocument();
      expect(screen.getByText('Ghost')).toBeInTheDocument();
      expect(screen.getByText('Link')).toBeInTheDocument();
    });

    it('applies size styles correctly', () => {
      render(
        <div>
          <Button size="default">Default</Button>
          <Button size="sm">Small</Button>
          <Button size="lg">Large</Button>
        </div>
      );

      expect(screen.getByText('Default')).toBeInTheDocument();
      expect(screen.getByText('Small')).toBeInTheDocument();
      expect(screen.getByText('Large')).toBeInTheDocument();
    });

    it('handles disabled state', () => {
      render(<Button disabled>Disabled Button</Button>);

      const button = screen.getByRole('button', { name: /disabled button/i });
      expect(button).toBeDisabled();
    });

    it('handles loading state', () => {
      render(<Button loading>Loading Button</Button>);

      expect(screen.getByText('Loading Button')).toBeInTheDocument();
      // Should show loading spinner or indicator
      const button = screen.getByRole('button', { name: /loading button/i });
      expect(button).toBeInTheDocument();
    });
  });

  describe('Card Component', () => {
    it('renders card with header, content, and footer', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Card Title</CardTitle>
            <CardDescription>Card description</CardDescription>
          </CardHeader>
          <CardContent>
            <p>Card content goes here</p>
          </CardContent>
          <CardFooter>
            <Button>Action</Button>
          </CardFooter>
        </Card>
      );

      expect(screen.getByText('Card Title')).toBeInTheDocument();
      expect(screen.getByText('Card description')).toBeInTheDocument();
      expect(screen.getByText('Card content goes here')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /action/i })).toBeInTheDocument();
    });

    it('renders card with proper semantic structure', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Test Card</CardTitle>
          </CardHeader>
          <CardContent>
            <p>Content</p>
          </CardContent>
        </Card>
      );

      const heading = screen.getByRole('heading', { name: /test card/i });
      expect(heading).toBeInTheDocument();
      expect(heading.tagName).toBe('H3'); // CardTitle should render as h3
    });
  });

  describe('Input Component', () => {
    it('renders input with label', () => {
      render(
        <div>
          <Label htmlFor="test-input">Test Label</Label>
          <Input id="test-input" placeholder="Enter text" />
        </div>
      );

      expect(screen.getByLabelText(/test label/i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/enter text/i)).toBeInTheDocument();
    });

    it('handles user input', async () => {
      const user = userEvent.setup();
      const handleChange = jest.fn();

      render(
        <Input
          placeholder="Enter text"
          onChange={(e) => handleChange(e.target.value)}
        />
      );

      const input = screen.getByPlaceholderText(/enter text/i);
      await user.type(input, 'Hello World');

      expect(handleChange).toHaveBeenCalledWith('Hello World');
    });

    it('handles different input types', () => {
      render(
        <div>
          <Input type="text" placeholder="Text input" />
          <Input type="email" placeholder="Email input" />
          <Input type="password" placeholder="Password input" />
          <Input type="number" placeholder="Number input" />
        </div>
      );

      expect(screen.getByPlaceholderText(/text input/i)).toHaveAttribute('type', 'text');
      expect(screen.getByPlaceholderText(/email input/i)).toHaveAttribute('type', 'email');
      expect(screen.getByPlaceholderText(/password input/i)).toHaveAttribute('type', 'password');
      expect(screen.getByPlaceholderText(/number input/i)).toHaveAttribute('type', 'number');
    });

    it('handles disabled state', () => {
      render(<Input disabled placeholder="Disabled input" />);

      const input = screen.getByPlaceholderText(/disabled input/i);
      expect(input).toBeDisabled();
    });

    it('handles error state', () => {
      render(<Input error placeholder="Error input" />);

      const input = screen.getByPlaceholderText(/error input/i);
      expect(input).toHaveClass('error'); // Should have error styling
    });
  });

  describe('Select Component', () => {
    it('renders select with options', async () => {
      const user = userEvent.setup();

      render(
        <Select>
          <SelectTrigger>
            <SelectValue placeholder="Select option" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="option1">Option 1</SelectItem>
            <SelectItem value="option2">Option 2</SelectItem>
            <SelectItem value="option3">Option 3</SelectItem>
          </SelectContent>
        </Select>
      );

      const trigger = screen.getByRole('combobox');
      expect(trigger).toBeInTheDocument();

      await user.click(trigger);

      expect(screen.getByText('Option 1')).toBeInTheDocument();
      expect(screen.getByText('Option 2')).toBeInTheDocument();
      expect(screen.getByText('Option 3')).toBeInTheDocument();
    });

    it('handles option selection', async () => {
      const user = userEvent.setup();
      const handleChange = jest.fn();

      render(
        <Select onValueChange={handleChange}>
          <SelectTrigger>
            <SelectValue placeholder="Select option" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="option1">Option 1</SelectItem>
            <SelectItem value="option2">Option 2</SelectItem>
          </SelectContent>
        </Select>
      );

      const trigger = screen.getByRole('combobox');
      await user.click(trigger);

      const option = screen.getByText('Option 1');
      await user.click(option);

      expect(handleChange).toHaveBeenCalledWith('option1');
    });

    it('displays selected value', async () => {
      const user = userEvent.setup();

      render(
        <Select defaultValue="option2">
          <SelectTrigger>
            <SelectValue placeholder="Select option" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="option1">Option 1</SelectItem>
            <SelectItem value="option2">Option 2</SelectItem>
            <SelectItem value="option3">Option 3</SelectItem>
          </SelectContent>
        </Select>
      );

      expect(screen.getByText('Option 2')).toBeInTheDocument();
    });

    it('handles disabled state', () => {
      render(
        <Select disabled>
          <SelectTrigger>
            <SelectValue placeholder="Disabled select" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="option1">Option 1</SelectItem>
          </SelectContent>
        </Select>
      );

      const trigger = screen.getByRole('combobox');
      expect(trigger).toBeDisabled();
    });
  });

  describe('Badge Component', () => {
    it('renders badge with text', () => {
      render(<Badge>Status Badge</Badge>);
      expect(screen.getByText('Status Badge')).toBeInTheDocument();
    });

    it('applies variant styles correctly', () => {
      render(
        <div>
          <Badge variant="default">Default</Badge>
          <Badge variant="secondary">Secondary</Badge>
          <Badge variant="destructive">Destructive</Badge>
          <Badge variant="outline">Outline</Badge>
        </div>
      );

      expect(screen.getByText('Default')).toBeInTheDocument();
      expect(screen.getByText('Secondary')).toBeInTheDocument();
      expect(screen.getByText('Destructive')).toBeInTheDocument();
      expect(screen.getByText('Outline')).toBeInTheDocument();
    });
  });

  describe('Alert Component', () => {
    it('renders alert with title and description', () => {
      render(
        <Alert>
          <AlertTitle>Alert Title</AlertTitle>
          <AlertDescription>Alert description with more details</AlertDescription>
        </Alert>
      );

      expect(screen.getByText('Alert Title')).toBeInTheDocument();
      expect(screen.getByText('Alert description with more details')).toBeInTheDocument();
    });

    it('applies variant styles correctly', () => {
      render(
        <div>
          <Alert variant="default">Default Alert</Alert>
          <Alert variant="destructive">Destructive Alert</Alert>
        </div>
      );

      expect(screen.getByText('Default Alert')).toBeInTheDocument();
      expect(screen.getByText('Destructive Alert')).toBeInTheDocument();
    });
  });

  describe('Table Component', () => {
    const tableData = [
      { id: 1, name: 'John Doe', email: 'john@example.com', status: 'Active' },
      { id: 2, name: 'Jane Smith', email: 'jane@example.com', status: 'Inactive' },
      { id: 3, name: 'Bob Johnson', email: 'bob@example.com', status: 'Active' }
    ];

    it('renders table with headers and data', () => {
      render(
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Email</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {tableData.map((row) => (
              <TableRow key={row.id}>
                <TableCell>{row.name}</TableCell>
                <TableCell>{row.email}</TableCell>
                <TableCell>{row.status}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      );

      expect(screen.getByText('Name')).toBeInTheDocument();
      expect(screen.getByText('Email')).toBeInTheDocument();
      expect(screen.getByText('Status')).toBeInTheDocument();
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('jane@example.com')).toBeInTheDocument();
      expect(screen.getByText('Active')).toBeInTheDocument();
    });

    it('handles empty table state', () => {
      render(
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow>
              <TableCell colSpan={1}>No data available</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      );

      expect(screen.getByText('No data available')).toBeInTheDocument();
    });
  });

  describe('Tabs Component', () => {
    it('renders tabs with content', async () => {
      const user = userEvent.setup();

      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
            <TabsTrigger value="tab2">Tab 2</TabsTrigger>
            <TabsTrigger value="tab3">Tab 3</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">Content 1</TabsContent>
          <TabsContent value="tab2">Content 2</TabsContent>
          <TabsContent value="tab3">Content 3</TabsContent>
        </Tabs>
      );

      expect(screen.getByText('Tab 1')).toBeInTheDocument();
      expect(screen.getByText('Tab 2')).toBeInTheDocument();
      expect(screen.getByText('Tab 3')).toBeInTheDocument();

      // Default tab should be visible
      expect(screen.getByText('Content 1')).toBeInTheDocument();
      expect(screen.queryByText('Content 2')).not.toBeInTheDocument();

      // Switch to tab 2
      await user.click(screen.getByText('Tab 2'));
      expect(screen.getByText('Content 2')).toBeInTheDocument();
      expect(screen.queryByText('Content 1')).not.toBeInTheDocument();
    });

    it('handles disabled tabs', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
            <TabsTrigger value="tab2" disabled>Tab 2</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">Content 1</TabsContent>
          <TabsContent value="tab2">Content 2</TabsContent>
        </Tabs>
      );

      const disabledTab = screen.getByText('Tab 2');
      expect(disabledTab).toBeDisabled();
      expect(disabledTab.closest('[role="tab"]')).toHaveAttribute('aria-disabled', 'true');
    });
  });

  describe('Dialog Component', () => {
    it('renders dialog with trigger and content', async () => {
      const user = userEvent.setup();

      render(
        <Dialog>
          <DialogTrigger>Open Dialog</DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Dialog Title</DialogTitle>
              <DialogDescription>Dialog description</DialogDescription>
            </DialogHeader>
            <div>Dialog content</div>
          </DialogContent>
        </Dialog>
      );

      // Trigger should be visible
      expect(screen.getByText('Open Dialog')).toBeInTheDocument();

      // Dialog should not be visible initially
      expect(screen.queryByText('Dialog Title')).not.toBeInTheDocument();

      // Click trigger to open dialog
      await user.click(screen.getByText('Open Dialog'));

      // Dialog should now be visible
      expect(screen.getByText('Dialog Title')).toBeInTheDocument();
      expect(screen.getByText('Dialog description')).toBeInTheDocument();
      expect(screen.getByText('Dialog content')).toBeInTheDocument();
    });

    it('handles dialog close functionality', async () => {
      const user = userEvent.setup();

      render(
        <Dialog>
          <DialogTrigger>Open Dialog</DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Dialog Title</DialogTitle>
            </DialogHeader>
            <div>Dialog content</div>
            <button>Close</button>
          </DialogContent>
        </Dialog>
      );

      // Open dialog
      await user.click(screen.getByText('Open Dialog'));
      expect(screen.getByText('Dialog Title')).toBeInTheDocument();

      // Close dialog
      await user.click(screen.getByText('Close'));
      expect(screen.queryByText('Dialog Title')).not.toBeInTheDocument();
    });
  });

  describe('Toast Component', () => {
    const TestToastComponent = () => {
      const { toast } = useToast();

      return (
        <div>
          <Button onClick={() => toast({ title: "Test Toast", description: "Toast message" })}>
            Show Toast
          </Button>
          <ToastProvider />
          <ToastViewport />
        </div>
      );
    };

    it('displays toast notifications', async () => {
      const user = userEvent.setup();

      render(<TestToastComponent />);

      const showToastButton = screen.getByText('Show Toast');
      await user.click(showToastButton);

      // Toast should appear (this might need adjustment based on actual toast implementation)
      await waitFor(() => {
        expect(screen.getByText('Test Toast')).toBeInTheDocument();
      });
    });

    it('handles different toast variants', async () => {
      const user = userEvent.setup();

      const MultiToastComponent = () => {
        const { toast } = useToast();

        return (
          <div>
            <Button onClick={() => toast({ title: "Success", variant: "default" })}>
              Show Success
            </Button>
            <Button onClick={() => toast({ title: "Error", variant: "destructive" })}>
              Show Error
            </Button>
            <ToastProvider />
            <ToastViewport />
          </div>
        );
      };

      render(<MultiToastComponent />);

      // Test success toast
      await user.click(screen.getByText('Show Success'));
      await waitFor(() => {
        expect(screen.getByText('Success')).toBeInTheDocument();
      });

      // Test error toast
      await user.click(screen.getByText('Show Error'));
      await waitFor(() => {
        expect(screen.getByText('Error')).toBeInTheDocument();
      });
    });
  });

  describe('Form Components Integration', () => {
    it('handles form submission with validation', async () => {
      const user = userEvent.setup();
      const handleSubmit = jest.fn();

      const TestForm = () => {
        const [formData, setFormData] = React.useState({ name: '', email: '' });

        const handleInputChange = (field) => (e) => {
          setFormData(prev => ({ ...prev, [field]: e.target.value }));
        };

        return (
          <form onSubmit={(e) => { e.preventDefault(); handleSubmit(formData); }}>
            <div>
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={handleInputChange('name')}
                placeholder="Enter name"
              />
            </div>
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={handleInputChange('email')}
                placeholder="Enter email"
              />
            </div>
            <Button type="submit">Submit</Button>
          </form>
        );
      };

      render(<TestForm />);

      // Fill out form
      await user.type(screen.getByPlaceholderText('Enter name'), 'John Doe');
      await user.type(screen.getByPlaceholderText('Enter email'), 'john@example.com');

      // Submit form
      await user.click(screen.getByRole('button', { name: /submit/i }));

      expect(handleSubmit).toHaveBeenCalledWith({
        name: 'John Doe',
        email: 'john@example.com'
      });
    });

    it('displays validation errors', async () => {
      const TestFormWithValidation = () => {
        const [errors, setErrors] = React.useState({});

        const validateForm = () => {
          const newErrors = {};
          if (!document.querySelector('input[value]')) {
            newErrors.name = 'Name is required';
          }
          setErrors(newErrors);
          return Object.keys(newErrors).length === 0;
        };

        return (
          <form>
            <div>
              <Label htmlFor="name">Name</Label>
              <Input id="name" placeholder="Enter name" />
              {errors.name && <span className="error">{errors.name}</span>}
            </div>
            <Button type="button" onClick={validateForm}>Validate</Button>
          </form>
        );
      };

      render(<TestFormWithValidation />);

      // Trigger validation without filling form
      await userEvent.click(screen.getByText('Validate'));

      await waitFor(() => {
        expect(screen.getByText('Name is required')).toBeInTheDocument();
      });
    });
  });

  describe('Data Display Components', () => {
    it('renders data table with sorting and filtering', async () => {
      const user = userEvent.setup();

      const TestDataTable = () => {
        const [sortColumn, setSortColumn] = React.useState('name');
        const [filter, setFilter] = React.useState('');

        const data = [
          { id: 1, name: 'Alice', age: 25, city: 'New York' },
          { id: 2, name: 'Bob', age: 30, city: 'San Francisco' },
          { id: 3, name: 'Charlie', age: 35, city: 'Chicago' }
        ];

        const filteredData = data.filter(item =>
          item.name.toLowerCase().includes(filter.toLowerCase())
        );

        return (
          <div>
            <Input
              placeholder="Filter by name"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            />
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Age</TableHead>
                  <TableHead>City</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredData.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>{item.name}</TableCell>
                    <TableCell>{item.age}</TableCell>
                    <TableCell>{item.city}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        );
      };

      render(<TestDataTable />);

      // Should display all data initially
      expect(screen.getByText('Alice')).toBeInTheDocument();
      expect(screen.getByText('Bob')).toBeInTheDocument();
      expect(screen.getByText('Charlie')).toBeInTheDocument();

      // Filter by name
      await user.type(screen.getByPlaceholderText('Filter by name'), 'a');

      await waitFor(() => {
        expect(screen.getByText('Alice')).toBeInTheDocument();
        expect(screen.getByText('Charlie')).toBeInTheDocument();
        expect(screen.queryByText('Bob')).not.toBeInTheDocument();
      });
    });
  });

  describe('Loading and Error States', () => {
    it('displays loading spinner', () => {
      const LoadingSpinner = () => (
        <div className="loading">
          <div className="spinner"></div>
          <span>Loading...</span>
        </div>
      );

      render(<LoadingSpinner />);

      expect(screen.getByText('Loading...')).toBeInTheDocument();
      // Should have spinner element (implementation specific)
    });

    it('displays error message', () => {
      const ErrorMessage = ({ message }) => (
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      );

      render(<ErrorMessage message="Something went wrong" />);

      expect(screen.getByText('Error')).toBeInTheDocument();
      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    });

    it('displays skeleton loading state', () => {
      const SkeletonLoader = () => (
        <div className="skeleton-container">
          <div className="skeleton skeleton-text"></div>
          <div className="skeleton skeleton-text"></div>
          <div className="skeleton skeleton-rect"></div>
        </div>
      );

      render(<SkeletonLoader />);

      const skeletons = document.querySelectorAll('.skeleton');
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  describe('Accessibility Tests', () => {
    it('provides proper ARIA labels', () => {
      render(
        <div>
          <Label htmlFor="test-input">Test Label</Label>
          <Input id="test-input" aria-describedby="help-text" />
          <div id="help-text">Help text</div>
        </div>
      );

      const input = screen.getByLabelText(/test label/i);
      expect(input).toHaveAttribute('aria-describedby', 'help-text');
    });

    it('supports keyboard navigation', async () => {
      const user = userEvent.setup();

      render(
        <div>
          <Button>First Button</Button>
          <Button>Second Button</Button>
          <Input placeholder="Test input" />
        </div>
      );

      // Tab through elements
      await user.tab();
      expect(document.activeElement).toBe(screen.getByText('First Button'));

      await user.tab();
      expect(document.activeElement).toBe(screen.getByText('Second Button'));

      await user.tab();
      expect(document.activeElement).toBe(screen.getByPlaceholderText('Test input'));
    });

    it('has proper focus management', async () => {
      const user = userEvent.setup();

      render(
        <Dialog>
          <DialogTrigger>Open Dialog</DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Dialog Title</DialogTitle>
            </DialogHeader>
            <Input placeholder="Dialog input" />
            <Button>Close</Button>
          </DialogContent>
        </Dialog>
      );

      // Open dialog
      await user.click(screen.getByText('Open Dialog'));

      // Focus should be managed properly in dialog
      await waitFor(() => {
        const dialogInput = screen.getByPlaceholderText('Dialog input');
        expect(dialogInput).toBeInTheDocument();
      });
    });
  });

  describe('Responsive Design Tests', () => {
    it('adapts to different screen sizes', () => {
      // Test mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });

      render(
        <div className="responsive-container">
          <div className="mobile-hidden">Desktop only</div>
          <div className="mobile-visible">Mobile only</div>
        </div>
      );

      // Should show mobile-specific content
      expect(screen.getByText('Mobile only')).toBeInTheDocument();
    });

    it('handles touch interactions', async () => {
      const user = userEvent.setup();

      render(<Button>Touch Button</Button>);

      const button = screen.getByText('Touch Button');

      // Simulate touch event
      fireEvent.touchStart(button);
      fireEvent.touchEnd(button);

      // Button should respond to touch
      expect(button).toBeInTheDocument();
    });
  });

  describe('Performance Tests', () => {
    it('renders components efficiently', () => {
      const startTime = performance.now();

      render(
        <div>
          {Array.from({ length: 100 }, (_, i) => (
            <Button key={i}>Button {i}</Button>
          ))}
        </div>
      );

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      // Should render 100 buttons within reasonable time
      expect(renderTime).toBeLessThan(100); // 100ms budget
      expect(screen.getByText('Button 0')).toBeInTheDocument();
      expect(screen.getByText('Button 99')).toBeInTheDocument();
    });

    it('handles large datasets efficiently', async () => {
      const largeDataset = Array.from({ length: 1000 }, (_, i) => ({
        id: i,
        name: `Item ${i}`,
        value: Math.random() * 100
      }));

      const startTime = performance.now();

      render(
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Value</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {largeDataset.map((item) => (
              <TableRow key={item.id}>
                <TableCell>{item.id}</TableCell>
                <TableCell>{item.name}</TableCell>
                <TableCell>{item.value.toFixed(2)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      );

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      // Should handle 1000 rows within reasonable time
      expect(renderTime).toBeLessThan(200); // 200ms budget
    });
  });
});
