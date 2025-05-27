import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { vi, describe, test, beforeEach, expect } from 'vitest';
import Dashboard from '../Dashboard';

// Mock framer-motion to avoid animation issues in tests
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>
  },
  AnimatePresence: ({ children }: any) => children
}));

// Mock Layout component
vi.mock('../../components/Layout', () => {
  return {
    default: function MockLayout({ children }: { children: React.ReactNode }) {
      return <div data-testid="layout">{children}</div>;
    }
  };
});

// Mock SidebarContext
vi.mock('../../contexts/SidebarContext', () => ({
  useSidebar: () => ({
    isCollapsed: false,
    setIsCollapsed: vi.fn(),
    toggleSidebar: vi.fn()
  })
}));

describe('Dashboard Repository CRUD Operations', () => {
  beforeEach(() => {
    // Reset any mocks
    vi.clearAllMocks();
  });

  test('should display repositories list with correct information', async () => {
    render(<Dashboard />);
    
    // Wait for the dashboard to load
    await waitFor(() => {
      expect(screen.getByText('📁 Repositories')).toBeInTheDocument();
    });

    // Check if repositories are displayed
    expect(screen.getByText('acme/frontend-app')).toBeInTheDocument();
    expect(screen.getByText('acme/backend-api')).toBeInTheDocument();
    
    // Check repository details
    expect(screen.getByText('Main frontend application built with React and TypeScript')).toBeInTheDocument();
    expect(screen.getByText('92/100')).toBeInTheDocument(); // Health score
  });

  test('should open add repository modal when floating button is clicked', async () => {
    const user = userEvent.setup();
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByTitle('Thêm repository mới')).toBeInTheDocument();
    });

    // Click the floating add button
    const addButton = screen.getByTitle('Thêm repository mới');
    await user.click(addButton);

    // Check if modal is opened
    expect(screen.getByText('➕ Thêm Repository Mới')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('e.g., acme/frontend-app')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('https://github.com/acme/frontend-app')).toBeInTheDocument();
  });

  test('should validate form fields when adding a repository', async () => {
    const user = userEvent.setup();
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByTitle('Thêm repository mới')).toBeInTheDocument();
    });

    // Open modal
    await user.click(screen.getByTitle('Thêm repository mới'));
    
    // Try to submit empty form
    const submitButton = screen.getByText('Thêm mới');
    await user.click(submitButton);

    // Check validation errors
    await waitFor(() => {
      expect(screen.getByText('Tên repository là bắt buộc')).toBeInTheDocument();
      expect(screen.getByText('URL repository là bắt buộc')).toBeInTheDocument();
    });
  });

  test('should validate URL format', async () => {
    const user = userEvent.setup();
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByTitle('Thêm repository mới')).toBeInTheDocument();
    });

    // Open modal
    await user.click(screen.getByTitle('Thêm repository mới'));
    
    // Fill in invalid URL
    const urlInput = screen.getByPlaceholderText('https://github.com/acme/frontend-app');
    await user.type(urlInput, 'invalid-url');
    
    const submitButton = screen.getByText('Thêm mới');
    await user.click(submitButton);

    // Check URL validation error
    await waitFor(() => {
      expect(screen.getByText('URL phải bắt đầu bằng http:// hoặc https://')).toBeInTheDocument();
    });
  });

  test('should validate repository name format', async () => {
    const user = userEvent.setup();
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByTitle('Thêm repository mới')).toBeInTheDocument();
    });

    // Open modal
    await user.click(screen.getByTitle('Thêm repository mới'));
    
    // Fill in invalid name with special characters
    const nameInput = screen.getByPlaceholderText('e.g., acme/frontend-app');
    await user.type(nameInput, 'invalid@name!');
    
    const submitButton = screen.getByText('Thêm mới');
    await user.click(submitButton);

    // Check name validation error
    await waitFor(() => {
      expect(screen.getByText('Tên repository chỉ được chứa chữ cái, số, dấu chấm, gạch dưới và dấu gạch ngang')).toBeInTheDocument();
    });
  });

  test('should successfully add a new repository', async () => {
    const user = userEvent.setup();
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByTitle('Thêm repository mới')).toBeInTheDocument();
    });

    // Open modal
    await user.click(screen.getByTitle('Thêm repository mới'));
    
    // Fill in valid data
    await user.type(screen.getByPlaceholderText('e.g., acme/frontend-app'), 'test/new-repo');
    await user.type(screen.getByPlaceholderText('https://github.com/acme/frontend-app'), 'https://github.com/test/new-repo');
    await user.type(screen.getByPlaceholderText('Mô tả ngắn gọn về repository...'), 'Test repository description');
    
    // Find language select by its current value
    const languageSelect = screen.getByDisplayValue('JavaScript');
    await user.selectOptions(languageSelect, 'Python');
    
    const submitButton = screen.getByText('Thêm mới');
    await user.click(submitButton);

    // Wait for submission
    await waitFor(() => {
      expect(screen.getByText('Đang lưu...')).toBeInTheDocument();
    });

    // Check if repository was added
    await waitFor(() => {
      expect(screen.getByText('test/new-repo')).toBeInTheDocument();
      expect(screen.getByText('Test repository description')).toBeInTheDocument();
    }, { timeout: 2000 });
  });

  test('should open edit modal when edit button is clicked', async () => {
    const user = userEvent.setup();
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('acme/frontend-app')).toBeInTheDocument();
    });

    // Find and click the edit button for the first repository
    const editButtons = screen.getAllByTitle('Chỉnh sửa repository');
    await user.click(editButtons[0]);

    // Check if edit modal is opened with pre-filled data
    expect(screen.getByText('✏️ Chỉnh sửa Repository')).toBeInTheDocument();
    expect(screen.getByDisplayValue('acme/frontend-app')).toBeInTheDocument();
    expect(screen.getByDisplayValue('https://github.com/acme/frontend-app')).toBeInTheDocument();
  });

  test('should update repository when editing', async () => {
    const user = userEvent.setup();
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('acme/frontend-app')).toBeInTheDocument();
    });

    // Click edit button
    const editButtons = screen.getAllByTitle('Chỉnh sửa repository');
    await user.click(editButtons[0]);

    // Update description
    const descriptionField = screen.getByPlaceholderText('Mô tả ngắn gọn về repository...');
    await user.clear(descriptionField);
    await user.type(descriptionField, 'Updated description for frontend app');
    
    // Submit changes
    const updateButton = screen.getByText('Cập nhật');
    await user.click(updateButton);

    // Wait for update to complete
    await waitFor(() => {
      expect(screen.getByText('Updated description for frontend app')).toBeInTheDocument();
    }, { timeout: 2000 });
  });

  test('should prevent duplicate repository names', async () => {
    const user = userEvent.setup();
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByTitle('Thêm repository mới')).toBeInTheDocument();
    });

    // Open add modal
    await user.click(screen.getByTitle('Thêm repository mới'));
    
    // Try to add repository with existing name
    await user.type(screen.getByPlaceholderText('e.g., acme/frontend-app'), 'acme/frontend-app');
    await user.type(screen.getByPlaceholderText('https://github.com/acme/frontend-app'), 'https://github.com/test/duplicate');
    
    const submitButton = screen.getByText('Thêm mới');
    await user.click(submitButton);

    // Check duplicate validation error
    await waitFor(() => {
      expect(screen.getByText('Repository với tên này đã tồn tại')).toBeInTheDocument();
    });
  });

  test('should show delete confirmation when delete button is clicked', async () => {
    const user = userEvent.setup();
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('acme/frontend-app')).toBeInTheDocument();
    });

    // Find and click the delete button
    const deleteButtons = screen.getAllByTitle('Xoá repository');
    await user.click(deleteButtons[0]);

    // Check if confirmation button appears
    await waitFor(() => {
      expect(screen.getByTitle('Xác nhận xoá')).toBeInTheDocument();
      expect(screen.getByTitle('Huỷ xoá')).toBeInTheDocument();
    });
  });

  test('should delete repository when confirmed', async () => {
    const user = userEvent.setup();
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('acme/frontend-app')).toBeInTheDocument();
    });

    // Click delete button
    const deleteButtons = screen.getAllByTitle('Xoá repository');
    await user.click(deleteButtons[0]);

    // Confirm deletion
    await waitFor(() => {
      expect(screen.getByTitle('Xác nhận xoá')).toBeInTheDocument();
    });
    
    const confirmButton = screen.getByTitle('Xác nhận xoá');
    await user.click(confirmButton);

    // Check if repository was removed
    await waitFor(() => {
      expect(screen.queryByText('acme/frontend-app')).not.toBeInTheDocument();
    });
  });

  test('should cancel delete when cancel button is clicked', async () => {
    const user = userEvent.setup();
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('acme/frontend-app')).toBeInTheDocument();
    });

    // Click delete button
    const deleteButtons = screen.getAllByTitle('Xoá repository');
    await user.click(deleteButtons[0]);

    // Cancel deletion
    await waitFor(() => {
      expect(screen.getByTitle('Huỷ xoá')).toBeInTheDocument();
    });
    
    const cancelButton = screen.getByTitle('Huỷ xoá');
    await user.click(cancelButton);

    // Check if repository is still there and confirmation buttons are gone
    expect(screen.getByText('acme/frontend-app')).toBeInTheDocument();
    expect(screen.queryByTitle('Xác nhận xoá')).not.toBeInTheDocument();
  });

  test('should close modal when clicking outside or X button', async () => {
    const user = userEvent.setup();
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByTitle('Thêm repository mới')).toBeInTheDocument();
    });

    // Open modal
    await user.click(screen.getByTitle('Thêm repository mới'));
    
    expect(screen.getByText('➕ Thêm Repository Mới')).toBeInTheDocument();

    // Click X button to close
    const closeButton = screen.getByRole('button', { name: '' }); // X button
    await user.click(closeButton);

    // Check if modal is closed
    await waitFor(() => {
      expect(screen.queryByText('➕ Thêm Repository Mới')).not.toBeInTheDocument();
    });
  });

  test('should update repository count in statistics when adding/deleting', async () => {
    const user = userEvent.setup();
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('📁 Repositories')).toBeInTheDocument();
    });

    // Check initial count (should be 6 repositories in mock data)
    const initialRepoCount = screen.getByText('6 repositories');
    expect(initialRepoCount).toBeInTheDocument();

    // Add a new repository
    await user.click(screen.getByTitle('Thêm repository mới'));
    await user.type(screen.getByPlaceholderText('e.g., acme/frontend-app'), 'test/count-repo');
    await user.type(screen.getByPlaceholderText('https://github.com/acme/frontend-app'), 'https://github.com/test/count-repo');
    await user.click(screen.getByText('Thêm mới'));

    // Wait for addition and check updated count
    await waitFor(() => {
      expect(screen.getByText('7 repositories')).toBeInTheDocument();
    }, { timeout: 2000 });

    // Delete a repository
    const deleteButtons = screen.getAllByTitle('Xoá repository');
    await user.click(deleteButtons[0]);
    
    await waitFor(() => {
      expect(screen.getByTitle('Xác nhận xoá')).toBeInTheDocument();
    });
    
    await user.click(screen.getByTitle('Xác nhận xoá'));

    // Check if count is updated after deletion
    await waitFor(() => {
      expect(screen.getByText('6 repositories')).toBeInTheDocument();
    });
  });

  test('should support all programming languages in dropdown', async () => {
    const user = userEvent.setup();
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByTitle('Thêm repository mới')).toBeInTheDocument();
    });

    // Open modal
    await user.click(screen.getByTitle('Thêm repository mới'));
    
    // Check all language options are available
    const languageSelect = screen.getByDisplayValue('JavaScript'); // Default language
    const languages = ['JavaScript', 'TypeScript', 'Python', 'Java', 'Go', 'Rust', 'C++', 'C#', 'PHP', 'Ruby', 'Swift', 'Kotlin'];
    
    languages.forEach(lang => {
      expect(screen.getByRole('option', { name: new RegExp(lang) })).toBeInTheDocument();
    });
  });
}); 