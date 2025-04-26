// src/app/page.tsx
'use client';

import { useState } from 'react';
import { ImageUploader } from '@/components/ImageUploader';
import { IngredientsList } from '@/components/IngredientsList';
import { AffinityModal } from '@/components/AffinityModal';

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [ingredients, setIngredients] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [ingredientAffinity, setIngredientAffinity] = useState<{ [key: string]: number }>({});
  const [showAffinityModal, setShowAffinityModal] = useState(false);

  const handleImageUpload = async (file: File) => {
    setIsLoading(true);
    setError(null);
    
    // 画像のプレビューURLを作成
    const imageUrl = URL.createObjectURL(file);
    setUploadedImage(imageUrl);
    
    try {
      const formData = new FormData();
      formData.append('image', file);
      
      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error('画像の分析に失敗しました');
      }
      
      const data = await response.json();
      setIngredients(data.ingredients);
    } catch (err) {
      setError(err instanceof Error ? err.message : '予期せぬエラーが発生しました');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setIngredients([]);
    setError(null);
    setIsLoading(false);
    if (uploadedImage) {
      URL.revokeObjectURL(uploadedImage);
      setUploadedImage(null);
    }
  };

  const handleSave = () => {
    // 現在の原材料の親密度を増やす
    const updatedAffinity = { ...ingredientAffinity };
    ingredients.forEach(ingredient => {
      updatedAffinity[ingredient] = Math.min(5, (updatedAffinity[ingredient] || 0) + 1);
    });
    setIngredientAffinity(updatedAffinity);
    setShowAffinityModal(true);
  };

  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-6xl mx-auto space-y-8">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-800">
            料理画像から原材料を分析
          </h1>
          <div className="flex gap-4">
            <button
              onClick={() => setShowAffinityModal(true)}
              className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
            >
              親密度表示
            </button>
            {ingredients.length > 0 && (
              <>
                <button
                  onClick={handleSave}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                >
                  保存
                </button>
                <button
                  onClick={handleReset}
                  className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                >
                  リセット
                </button>
              </>
            )}
          </div>
        </div>
        
        <div className="space-y-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <ImageUploader 
              onImageUpload={handleImageUpload} 
              isLoading={isLoading}
              onReset={handleReset}
            />
          </div>
          
          {uploadedImage && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="relative w-full h-[400px]">
                <img
                  src={uploadedImage}
                  alt="アップロードされた画像"
                  className="w-full h-full object-contain rounded-lg"
                />
              </div>
            </div>
          )}
          
          {isLoading && (
            <div className="flex justify-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
          )}
          
          {error && (
            <div className="text-red-500 text-center bg-white p-4 rounded-lg shadow-lg">
              {error}
            </div>
          )}
          
          {!isLoading && ingredients.length > 0 && (
            <IngredientsList 
              ingredients={ingredients} 
              ingredientAffinity={ingredientAffinity}
              setIngredientAffinity={setIngredientAffinity}
            />
          )}
        </div>

        {showAffinityModal && (
          <AffinityModal
            isOpen={showAffinityModal}
            onClose={() => setShowAffinityModal(false)}
            ingredientAffinity={ingredientAffinity}
          />
        )}
      </div>
    </main>
  );
}
