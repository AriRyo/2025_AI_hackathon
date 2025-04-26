import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const image = formData.get('image') as File;

    if (!image) {
      return NextResponse.json(
        { error: '画像がアップロードされていません' },
        { status: 400 }
      );
    }

    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/analyze-dish`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('バックエンドからの応答が不正です');
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('画像分析エラー:', error);
    return NextResponse.json(
      { error: '画像の分析に失敗しました' },
      { status: 500 }
    );
  }
} 