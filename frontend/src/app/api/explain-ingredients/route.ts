import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { ingredients } = await request.json();

    if (!ingredients || !Array.isArray(ingredients)) {
      return NextResponse.json(
        { error: '食材リストが不正です' },
        { status: 400 }
      );
    }

    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/explain-ingredients`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ ingredients }),
    });


    const data = await response.json();
    console.log(data)
    return NextResponse.json(data);
  } catch (error) {
    console.error('食材情報取得エラー:', error);
    return NextResponse.json(
      { error: '食材情報の取得に失敗しました' },
      { status: 500 }
    );
  }
} 