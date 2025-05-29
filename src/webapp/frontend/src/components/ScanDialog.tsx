import React, { useState } from 'react';
import { Scan, ScanType } from '../types';
import { repositoryApi } from '../services/repositoryApi';

interface ScanDialogProps {
  repositoryId: string;
  onScanCreated: (scan: Scan) => void;
  onClose: () => void;
}

export default function ScanDialog({ repositoryId, onScanCreated, onClose }: ScanDialogProps) {
  const [scanType, setScanType] = useState<ScanType>('full');
  const [prNumber, setPrNumber] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const newScan = await repositoryApi.createScan(repositoryId, {
        type: scanType,
        pr_number: scanType === 'pr' ? parseInt(prNumber) : undefined
      });
      
      onScanCreated(newScan);
      onClose();
    } catch (error) {
      console.error('Failed to create scan:', error);
      alert('Failed to create scan. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">New Scan</h2>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <h3 className="text-sm font-medium mb-2">Scan Type</h3>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="scanType"
                  value="full"
                  checked={scanType === 'full'}
                  onChange={() => setScanType('full')}
                  className="mr-2"
                />
                <span>Full Repository Scan</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="scanType"
                  value="pr"
                  checked={scanType === 'pr'}
                  onChange={() => setScanType('pr')}
                  className="mr-2"
                />
                <span>Pull Request Scan</span>
              </label>
            </div>
          </div>
          
          {scanType === 'pr' && (
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">
                PR Number
                <input
                  type="number"
                  value={prNumber}
                  onChange={(e) => setPrNumber(e.target.value)}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="Enter PR number"
                  required
                />
              </label>
            </div>
          )}
          
          <div className="flex justify-end space-x-2 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Starting Scan...' : 'Start Scan'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
} 