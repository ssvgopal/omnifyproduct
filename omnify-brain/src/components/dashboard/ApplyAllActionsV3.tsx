'use client';

/**
 * Apply All Actions V3 - FACE Wireframe Component
 * 
 * Batch action button per FACE_Wireframes_v1:
 * - "Apply All Recommendations" button
 * - Copy to clipboard option
 * - Confirmation modal before execution
 */

import { useState } from 'react';
import { CuriosityOutputV3 } from '@/lib/types';
import { Zap, Copy, Check, Loader2, AlertCircle } from 'lucide-react';

interface ApplyAllActionsV3Props {
  curiosity: CuriosityOutputV3;
  onApplyAll?: () => Promise<void>;
}

export function ApplyAllActionsV3({ curiosity, onApplyAll }: ApplyAllActionsV3Props) {
  const [isApplying, setIsApplying] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [copied, setCopied] = useState(false);
  const [result, setResult] = useState<'success' | 'error' | null>(null);

  const { topActions, totalOpportunityFormatted } = curiosity;

  const handleApplyAll = async () => {
    if (!onApplyAll) {
      // Simulation mode - just show success
      setIsApplying(true);
      await new Promise(resolve => setTimeout(resolve, 1500));
      setIsApplying(false);
      setShowConfirm(false);
      setResult('success');
      setTimeout(() => setResult(null), 3000);
      return;
    }

    setIsApplying(true);
    try {
      await onApplyAll();
      setResult('success');
    } catch (error) {
      setResult('error');
    } finally {
      setIsApplying(false);
      setShowConfirm(false);
      setTimeout(() => setResult(null), 3000);
    }
  };

  const handleCopyToClipboard = async () => {
    const text = topActions.map((action, i) => 
      `${i + 1}. ${action.title}\n   Impact: ${action.impactFormatted}\n   ${action.description}`
    ).join('\n\n');

    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-white rounded-lg border shadow-sm p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-semibold text-gray-900">Quick Actions</h3>
          <p className="text-sm text-gray-500">
            {topActions.length} recommendations • {totalOpportunityFormatted} potential
          </p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        {/* Apply All Button */}
        <button
          onClick={() => setShowConfirm(true)}
          disabled={isApplying || topActions.length === 0}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isApplying ? (
            <>
              <Loader2 className="h-5 w-5 animate-spin" />
              Applying...
            </>
          ) : (
            <>
              <Zap className="h-5 w-5" />
              Apply All Recommendations
            </>
          )}
        </button>

        {/* Copy Button */}
        <button
          onClick={handleCopyToClipboard}
          className="flex items-center justify-center gap-2 px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          title="Copy to clipboard"
        >
          {copied ? (
            <Check className="h-5 w-5 text-green-600" />
          ) : (
            <Copy className="h-5 w-5 text-gray-600" />
          )}
        </button>
      </div>

      {/* Result Message */}
      {result && (
        <div className={`mt-3 p-3 rounded-lg flex items-center gap-2 ${
          result === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
        }`}>
          {result === 'success' ? (
            <>
              <Check className="h-5 w-5" />
              <span>All recommendations applied successfully!</span>
            </>
          ) : (
            <>
              <AlertCircle className="h-5 w-5" />
              <span>Failed to apply recommendations. Please try again.</span>
            </>
          )}
        </div>
      )}

      {/* Confirmation Modal */}
      {showConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Apply All Recommendations?
            </h3>
            <p className="text-gray-600 mb-4">
              This will execute {topActions.length} actions with an estimated impact of {totalOpportunityFormatted}.
            </p>

            {/* Action Summary */}
            <div className="bg-gray-50 rounded-lg p-3 mb-4 max-h-40 overflow-y-auto">
              {topActions.map((action, i) => (
                <div key={action.id} className="text-sm py-1 border-b last:border-0">
                  <span className="font-medium">{i + 1}. {action.title}</span>
                  <span className="text-green-600 ml-2">{action.impactFormatted}</span>
                </div>
              ))}
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowConfirm(false)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleApplyAll}
                disabled={isApplying}
                className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50"
              >
                {isApplying ? 'Applying...' : 'Confirm & Apply'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
