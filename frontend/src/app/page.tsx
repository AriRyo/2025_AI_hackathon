// src/app/page.tsx
'use client';

import { useState } from 'react';
import { ImageUploader } from '@/components/ImageUploader';
import { IngredientsList } from '@/components/IngredientsList';

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [ingredients, setIngredients] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);

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

  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-6xl mx-auto space-y-8">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-800">
            料理画像から原材料を分析
          </h1>
          {ingredients.length > 0 && (
            <button
              onClick={handleReset}
              className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
            >
              リセット
            </button>
          )}
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
            <IngredientsList ingredients={ingredients} />
          )}
        </div>
      </div>
    </main>
  );
}
