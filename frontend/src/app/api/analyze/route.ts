import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    // 実際のAPIでは、ここで画像データを処理します
    // 今回はモックデータを返します
    const mockIngredients = ['豚肉', '人参', 'ピーマン', '玉ねぎ', '赤パプリカ'];
    
    // 2秒の遅延を追加して、実際のAPIのような動作をシミュレート
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    return NextResponse.json({ ingredients: mockIngredients });
  } catch (error) {
    return NextResponse.json(
      { error: '画像の分析に失敗しました' },
      { status: 500 }
    );
  }
} 