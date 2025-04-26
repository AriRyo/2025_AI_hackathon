import React, { useState, useEffect } from 'react';

interface IngredientModalProps {
  isOpen: boolean;
  onClose: () => void;
  ingredient: string;
  imagePath: string;
  affinity: number;
  onAffinityChange: (newAffinity: number) => void;
}

interface IngredientInfo {
  食材の名前: string;
  食材の育った環境: string;
  食材の豆知識: string;
}

export const IngredientModal = ({ 
  isOpen, 
  onClose, 
  ingredient, 
  imagePath,
  affinity,
  onAffinityChange
}: IngredientModalProps) => {
  const [ingredientInfo, setIngredientInfo] = useState<IngredientInfo | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchIngredientInfo = async () => {
      if (isOpen && ingredient) {
        setIsLoading(true);
        try {
          const response = await fetch('http://localhost:8000/explain-ingredients', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              ingredients: [ingredient]
            }),
          });
          
          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || '食材情報の取得に失敗しました');
          }
          
          const data = await response.json();
          if (!data || !data[0]) {
            throw new Error('食材情報が見つかりませんでした');
          }
          
          setIngredientInfo(data[0]);
        } catch (error) {
          console.error('食材情報の取得に失敗しました:', error);
          setIngredientInfo(null);
        } finally {
          setIsLoading(false);
        }
      }
    };

    fetchIngredientInfo();
  }, [isOpen, ingredient]);

  if (!isOpen) return null;

  const renderHearts = (count: number) => {
    return Array.from({ length: count }, (_, i) => (
      <span key={i} className="text-red-500 text-2xl">❤️</span>
    ));
  };

  return (
    <div className="fixed inset-0 bg-opacity-30 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-white/95 rounded-lg p-8 max-w-xl w-full mx-4 shadow-2xl">
        <div className="flex justify-between items-start mb-6">
          <h2 className="text-3xl font-bold text-gray-800">{ingredient}</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <div className="relative w-full h-80">
          <img
            src={imagePath}
            alt={ingredient}
            className="w-full h-full object-contain rounded-lg"
          />
        </div>
          
        <div className="space-y-6">
          {isLoading ? (
            <div className="flex justify-center items-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
            </div>
          ) : ingredientInfo ? (
            <>
              <div>
                <h3 className="text-xl font-semibold text-gray-700 mb-3">食材の育った環境</h3>
                <p className="text-gray-600 leading-relaxed">
                  {ingredientInfo.食材の育った環境}
                </p>
              </div>
                
              <div>
                <h3 className="text-xl font-semibold text-gray-700 mb-3">食材の豆知識</h3>
                <p className="text-gray-600 leading-relaxed">
                  {ingredientInfo.食材の豆知識}
                </p>
              </div>
            </>
          ) : (
            <div className="text-center text-gray-500">
              食材情報の取得に失敗しました
            </div>
          )}

          <div>
            <h3 className="text-xl font-semibold text-gray-700 mb-3">親密度</h3>
            <div className="flex items-center gap-4">
              <div className="flex gap-1">
                {renderHearts(affinity)}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => onAffinityChange(Math.max(0, affinity - 1))}
                  className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300 transition-colors"
                >
                  -
                </button>
                <button
                  onClick={() => onAffinityChange(Math.min(5, affinity + 1))}
                  className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300 transition-colors"
                >
                  +
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}; 