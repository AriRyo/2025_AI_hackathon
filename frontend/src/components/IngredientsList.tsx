import { useState } from 'react';
import { IngredientModal } from './IngredientModal';

interface IngredientsListProps {
  ingredients: string[];
}

// 食材名と画像の対応表
const ingredientImages: { [key: string]: string } = {
  '豚肉': '/images/pork.png',
  '人参': '/images/carrot.png',
  'ピーマン': '/images/pepper.png',
  '玉ねぎ': '/images/onion.png',
  '赤パプリカ': '/images/red_pepper.png',
};

export const IngredientsList = ({ ingredients }: IngredientsListProps) => {
  const [selectedIngredient, setSelectedIngredient] = useState<string | null>(null);

  const handleCardClick = (ingredient: string) => {
    setSelectedIngredient(ingredient);
  };

  const handleCloseModal = () => {
    setSelectedIngredient(null);
  };

  return (
    <div className="w-full max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">原材料</h2>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {ingredients.map((ingredient, index) => (
          <div
            key={index}
            onClick={() => handleCardClick(ingredient)}
            className="flex flex-col items-center justify-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer transform hover:scale-105"
          >
            <div className="w-24 h-24 mb-2 relative">
              <img
                src={ingredientImages[ingredient] || '/images/default.png'}
                alt={ingredient}
                className="w-full h-full object-contain"
              />
            </div>
            <span className="text-gray-700 font-medium text-center">{ingredient}</span>
          </div>
        ))}
      </div>

      {selectedIngredient && (
        <IngredientModal
          isOpen={true}
          onClose={handleCloseModal}
          ingredient={selectedIngredient}
          imagePath={ingredientImages[selectedIngredient] || '/images/default.png'}
        />
      )}
    </div>
  );
}; 