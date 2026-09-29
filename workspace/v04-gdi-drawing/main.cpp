#include <afxwin.h>

class CMyApp : public CWinApp {
public:
    virtual BOOL InitInstance();
};

class CMainWnd : public CFrameWnd {
public:
    CMainWnd() { Create(NULL, "GDI 绘图"); }
    afx_msg void OnPaint();
    DECLARE_MESSAGE_MAP()
};

BEGIN_MESSAGE_MAP(CMainWnd, CFrameWnd)
    ON_WM_PAINT()
END_MESSAGE_MAP()

// ================== TODO: 按教材 2.5~2.6 完成绘图 ==================
void CMainWnd::OnPaint()
{
    CPaintDC dc(this);      // 绑定 WM_PAINT 的设备环境

    // TODO: 用 dc 画一条直线(MoveTo + LineTo)
    // TODO: 画一个矩形(dc.Rectangle)
    // TODO: 画一个椭圆(dc.Ellipse)
}
// ==================================================================

BOOL CMyApp::InitInstance()
{
    CMainWnd* wnd = new CMainWnd();
    m_pMainWnd = wnd;
    wnd->ShowWindow(SW_SHOW);
    wnd->UpdateWindow();
    return TRUE;
}

CMyApp theApp;                      // 全局唯一的应用程序对象
