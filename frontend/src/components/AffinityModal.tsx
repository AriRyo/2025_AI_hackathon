interface AffinityModalProps {
  isOpen: boolean;
  onClose: () => void;
  ingredientAffinity: { [key: string]: number };
}

export const AffinityModal = ({ isOpen, onClose, ingredientAffinity }: AffinityModalProps) => {
  if (!isOpen) return null;

  const renderHearts = (count: number) => {
    return Array.from({ length: count }, (_, i) => (
      <span key={i} className="text-red-500 text-2xl">❤️</span>
    ));
  };

  return (
    <div className="fixed inset-0  bg-opacity-30 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-white/95 rounded-lg p-8 max-w-xl w-full mx-4 shadow-2xl">
        <div className="flex justify-between items-start mb-6">
          <h2 className="text-3xl font-bold text-gray-800">食材との親密度</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <div className="space-y-4">
          {Object.entries(ingredientAffinity).map(([ingredient, affinity]) => (
            <div key={ingredient} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <span className="text-lg font-medium text-gray-700">{ingredient}</span>
              <div className="flex gap-1">
                {renderHearts(affinity)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}; 