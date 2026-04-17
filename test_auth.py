"""
FastAPI-Users 测试脚本
"""
import asyncio
import httpx
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


async def test_register(email: str, password: str) -> Dict[str, Any]:
    """测试用户注册"""
    print("\n" + "=" * 50)
    print("1. 测试用户注册")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": email,
                "password": password,
                "username": "testuser",
                "full_name": "测试用户",
                "phone": "13800138000"
            }
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"注册成功！用户ID: {data['id']}")
            return data
        else:
            print(f"注册失败: {response.text}")
            return {}


async def test_login(email: str, password: str) -> Dict[str, Any]:
    """测试用户登录"""
    print("\n" + "=" * 50)
    print("2. 测试用户登录")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/auth/jwt/login",
            data={
                "username": email,
                "password": password
            }
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"登录成功！Token 类型: {data['token_type']}")
            print(f"Access Token (前30字符): {data['access_token'][:30]}...")
            return data
        else:
            print(f"登录失败: {response.text}")
            return {}


async def test_get_user(token: str) -> Dict[str, Any]:
    """测试获取当前用户信息"""
    print("\n" + "=" * 50)
    print("3. 测试获取当前用户信息")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/users/me",
            headers={
                "Authorization": f"Bearer {token}"
            }
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"用户邮箱: {data['email']}")
            print(f"用户名: {data.get('username')}")
            print(f"全名: {data.get('full_name')}")
            return data
        else:
            print(f"获取失败: {response.text}")
            return {}


async def test_update_user(token: str) -> Dict[str, Any]:
    """测试更新用户信息"""
    print("\n" + "=" * 50)
    print("4. 测试更新用户信息")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{BASE_URL}/users/me",
            headers={
                "Authorization": f"Bearer {token}"
            },
            json={
                "full_name": "更新后的姓名",
                "phone": "13900139000"
            }
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"更新成功！新全名: {data['full_name']}")
            print(f"新电话: {data['phone']}")
            return data
        else:
            print(f"更新失败: {response.text}")
            return {}


async def main():
    """主测试流程"""
    print("\n" + "=" * 50)
    print("FastAPI-Users 功能测试")
    print("=" * 50)
    
    test_email = "test@example.com"
    test_password = "TestPassword123"
    
    try:
        # 1. 注册
        user_data = await test_register(test_email, test_password)
        if not user_data:
            print("\n注册失败，终止测试")
            return
        
        # 2. 登录
        auth_data = await test_login(test_email, test_password)
        if not auth_data:
            print("\n登录失败，终止测试")
            return
        
        token = auth_data.get("access_token")
        
        # 3. 获取用户信息
        await test_get_user(token)
        
        # 4. 更新用户信息
        await test_update_user(token)
        
        print("\n" + "=" * 50)
        print("✅ 所有测试完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")


if __name__ == "__main__":
    print("\n⚠️  请确保后端服务已启动 (python backend/app/main.py)")
    input("\n按回车键开始测试...")
    
    asyncio.run(main())
