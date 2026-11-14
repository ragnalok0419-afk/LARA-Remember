package com.remember.lara;

import android.Manifest;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.speech.RecognizerIntent;
import android.speech.tts.TextToSpeech;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.Toast;
import java.util.ArrayList;
import java.util.Locale;
import org.json.JSONObject;

public class MainActivity extends Activity {
    private WebView web;
    private TextToSpeech tts;
    private static final int SPEECH_REQ=400;
    private String base;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        web=new WebView(this);setContentView(web);
        web.getSettings().setJavaScriptEnabled(true);
        web.getSettings().setDomStorageEnabled(true);
        web.setWebChromeClient(new WebChromeClient());
        web.setWebViewClient(new WebViewClient(){
            @Override public boolean shouldOverrideUrlLoading(WebView view,WebResourceRequest request){
                String url=request.getUrl().toString();
                if(!url.startsWith(base)){
                    try {startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse(url)));} catch(Exception ex) {toast("외부 링크를 열 수 없어요.");}
                    return true;
                }
                return false;
            }
            @Override public void onReceivedError(WebView view, WebResourceRequest request, android.webkit.WebResourceError error){
                if(request.isForMainFrame())toast("PC 서버에 접속하지 못했어요. 서버 주소와 같은 Wi-Fi를 확인하세요.");
            }
        });
        web.addJavascriptInterface(new Bridge(),"AndroidLara");
        tts=new TextToSpeech(this,status->{if(status==TextToSpeech.SUCCESS&&tts!=null)tts.setLanguage(Locale.KOREAN);});
        String saved=getPreferences(MODE_PRIVATE).getString("server","");
        if(saved.isEmpty())chooseServer();else loadServer(saved);
    }
    private void toast(String text){runOnUiThread(()->Toast.makeText(this,text,Toast.LENGTH_LONG).show());}
    private void loadServer(String value){
        String addr=value.trim().replaceAll("/+$","");
        if(!addr.matches("https?://[^/\\s]+(:[0-9]+)?")){toast("주소 형식을 확인해 주세요. 예: http://192.168.0.5:8765");chooseServer();return;}
        base=addr+"/";
        getPreferences(MODE_PRIVATE).edit().putString("server",addr).apply();
        web.loadUrl(base);
    }
    private void chooseServer(){
        EditText edit=new EditText(this);
        edit.setSingleLine(true);edit.setText(getPreferences(MODE_PRIVATE).getString("server","http://192.168.0.2:8765"));
        LinearLayout wrapper=new LinearLayout(this); wrapper.setPadding(36,12,36,0);wrapper.addView(edit);
        new AlertDialog.Builder(this).setTitle("LARA PC 서버 연결")
          .setMessage("PC에서 LARA 실행 파일을 켠 뒤 같은 Wi-Fi에 연결하세요. PC의 IPv4 주소를 아래에 입력하세요.\n예: http://192.168.0.5:8765")
          .setView(wrapper).setPositiveButton("연결",(d,w)->loadServer(edit.getText().toString()))
          .setNegativeButton("종료",(d,w)->finish()).setCancelable(false).show();
    }
    class Bridge {
        @JavascriptInterface public void speak(String text){runOnUiThread(()->{if(tts!=null)tts.speak(text,TextToSpeech.QUEUE_FLUSH,null,"lara");});}
        @JavascriptInterface public void listen(){runOnUiThread(()->{
            if(checkSelfPermission(Manifest.permission.RECORD_AUDIO)!=PackageManager.PERMISSION_GRANTED){
                requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO},501);return;
            }
            startSpeech();
        });}
        @JavascriptInterface public void openExternal(String url){
            if(url!=null&&url.startsWith("https://www.google.com/maps/"))runOnUiThread(()->{
                try{startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse(url)));}catch(Exception ex){toast("지도 앱을 열 수 없어요.");}
            });
        }
        @JavascriptInterface public void configureServer(){runOnUiThread(()->chooseServer());}
    }
    @Override public void onRequestPermissionsResult(int req,String[] permissions,int[] results){
        super.onRequestPermissionsResult(req,permissions,results);
        if(req==501 && results.length>0 && results[0]==PackageManager.PERMISSION_GRANTED)startSpeech();
        else if(req==501)toast("음성 입력을 사용하려면 마이크 권한이 필요해요.");
    }
    private void startSpeech(){
        try{
            Intent intent=new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE,"ko-KR");
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
            startActivityForResult(intent,SPEECH_REQ);
        }catch(Exception ex){toast("휴대폰에 한국어 음성 인식 서비스가 필요해요.");}
    }
    @Override protected void onActivityResult(int req,int result,Intent data){
        super.onActivityResult(req,result,data);
        if(req==SPEECH_REQ&&result==RESULT_OK&&data!=null){
            ArrayList<String> words=data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS);
            if(words!=null&&!words.isEmpty())web.evaluateJavascript("window.laraSpeechResult("+JSONObject.quote(words.get(0))+")",null);
        }
    }
    @Override public void onBackPressed(){if(web.canGoBack())web.goBack();else new AlertDialog.Builder(this).setMessage("PC 서버 주소를 바꿀까요?").setPositiveButton("주소 변경",(d,w)->chooseServer()).setNegativeButton("취소",null).show();}
    @Override protected void onDestroy(){if(tts!=null){tts.stop();tts.shutdown();}if(web!=null)web.destroy();super.onDestroy();}
}
