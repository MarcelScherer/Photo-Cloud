package com.photocloud.marcel.photocloud;

import android.app.ProgressDialog;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Environment;
import android.provider.MediaStore;
import android.provider.Settings;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.Toast;

import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.Socket;
import java.net.URL;

public class MainActivity extends AppCompatActivity {

    static int SERVER_ID = 1302;
    static String SERVER_IP = "ms-schneppenbach.spdns.de";
    static int SERVER_PORT  = 4000;

    Button send_photo_button;    /* button for send the photo */
    Button take_photo_button;    /* button for take a new photo */
    ImageView akt_photo;         /* image view to show the taken photo */
    Intent camera_intent;        /* intent to start the camera*/
    Bitmap photo_bitmap;         /* bitmap for show the photo in view */
    int server_response;      /* server response string */
    ProgressDialog uploadDialog; /* dialgog for upload pogress bar*/


    /* storage path of photo */

    //File photo_file = new File(Environment.getExternalStorageDirectory() + "/PhotoCloud/Bild.png");
    File photo_file = new File(Environment.getExternalStorageDirectory() + "/PhotoCloud/Bild.png");
    File foulder = new File(Environment.getExternalStorageDirectory() + "/PhotoCloud/");

    public Button getSend_photo_button() {
        return send_photo_button;
    }

    Uri photo_uri = Uri.fromFile(photo_file);

    /* control code after intent response */
    int camera_code = 13;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        /* conect instants with items in xml */
        send_photo_button = (Button) findViewById(R.id.send_photo);
        take_photo_button = (Button) findViewById(R.id.take_photo);
        akt_photo         = (ImageView) findViewById(R.id.akt_image);

        foulder.mkdirs();

        /* action button "take photo" */
        take_photo_button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                try {
                    camera_intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
                    camera_intent.putExtra(MediaStore.EXTRA_OUTPUT, photo_uri);
                    startActivityForResult(camera_intent, camera_code);
                } catch (Exception e) {
                    e.printStackTrace();
                    Toast.makeText(getApplicationContext(), "Kammera nicht unterstützt", Toast.LENGTH_LONG).show();
                }
            }
        });

        /* action button "send photo" */
        send_photo_button.setOnClickListener(new View.OnClickListener(){
             @Override
             public void onClick(View v) {
                 if(photo_file.exists() &&  internetAvailable()) {
                     uploadDialog = new ProgressDialog(MainActivity.this);
                     uploadDialog.setTitle("Bild wird hochgeladen...");
                     uploadDialog.setMessage("Bitte warten.");
                     uploadDialog.setProgressStyle(ProgressDialog.STYLE_HORIZONTAL);
                     Log.d("Meine App", "State0");
                     uploadDialog.show();
                     Log.d("Meine App", "State0");
                     new UploadImageAsyncTask().execute();
                 }else if(!internetAvailable()){
                     Toast.makeText(getApplicationContext(), "Kein Internet vorhanden", Toast.LENGTH_LONG).show();
                 }else{
                     Toast.makeText(getApplicationContext(), "Kein Photo vorhanden", Toast.LENGTH_LONG).show();
                 }
             }
        });
    }

    /* function is running after intent (cammera app) is finished */
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {

        if (requestCode == RESULT_OK && resultCode == camera_code){
            photo_bitmap = BitmapFactory.decodeFile(photo_file.getAbsolutePath());
            akt_photo.setImageBitmap(photo_bitmap);
        }
        super.onActivityResult(requestCode, resultCode, data);
    }

    @Override
    public void onResume(){
        super.onResume();
        try {
            photo_bitmap = BitmapFactory.decodeFile(photo_file.getAbsolutePath());
            Log.d("Meine App", "Filehight: " + Integer.toString(photo_bitmap.getHeight()));
            Log.d("Meine App", "Fileswidth: " + Integer.toString(photo_bitmap.getWidth()));
            akt_photo.setImageBitmap(photo_bitmap);
        } catch (Exception e) {
            Toast.makeText(getApplicationContext(), "Photo laden nicht möglich", Toast.LENGTH_LONG).show();
            e.printStackTrace();
        }

    }

    /* a new task for upload the photo */
    public class UploadImageAsyncTask extends AsyncTask{
        /* handles everthing in the async task */
        @Override
        protected Object doInBackground(Object[] params) {
            Log.d("Meine App", "State01");
            server_response = 1;
            try {
			    /* conncet to server */
                Socket socket_client = new Socket(SERVER_IP, SERVER_PORT);
                Log.d("Meine App", "Start connection to " + SERVER_IP + " on Port " + Integer.toString(SERVER_PORT));

			    /* create input- and outputstream */
                DataOutputStream socket_output = new DataOutputStream(socket_client.getOutputStream());
                DataInputStream socket_input = new DataInputStream(socket_client.getInputStream());

			    /* send  Server-ID */
                socket_output.writeInt(SERVER_ID);
                Log.d("Meine App", "Send Server-ID: " + Integer.toString(SERVER_ID));

			    /* received seed for key calculation */
                int seed = socket_input.readInt();
                Log.d("Meine App", "Received Seed: " + Integer.toString(seed));

			    /* calculate key and send it back */
                int key = ((seed + 12) * 2) + 123;
                socket_output.writeInt(key);
                Log.d("Meine App", "Calculate Key: " + Integer.toString(key));
                Log.d("Meine App", "Send Key ...");

                /* if key correct send file size*/
                if (socket_input.readInt() == 1) {
                    Long Filesize = photo_file.length();
                    socket_output.writeLong(Filesize);
                    Log.d("Meine App", "Send Filesize in bytes: " + Long.toString(Filesize));
                    uploadDialog.setMax(Filesize.intValue());
                	/* send file*/
                    try {
                        FileInputStream file_input = new FileInputStream(photo_file);
                        byte[] send_byte = new byte[1024];
                        int buf_size = 0;
                        Long send_data_size = 0L;
                        while (Filesize > 0) {
                            if (Filesize > 1024) {
                                buf_size = file_input.read(send_byte, 0, 1024);
                                socket_output.write(send_byte, 0, buf_size);
                                Filesize = Filesize - buf_size;
                                send_data_size = send_data_size + buf_size;
                                uploadDialog.setProgress(send_data_size.intValue());
                            } else {
                                buf_size = file_input.read(send_byte, 0, (Filesize.intValue()));
                                socket_output.write(send_byte, 0, buf_size);
                                Filesize = Filesize - buf_size;
                                send_data_size = send_data_size + buf_size;
                                uploadDialog.setProgress(send_data_size.intValue());
                            }
                        }
                        file_input.close();
                        server_response = 2;
                    } catch (IOException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }
                } else {

                }
                socket_output.close();
                Log.d("Meine App", "Close Socket ...");

            } catch (IOException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }
            return null;
        }


        @Override
        /* starts after asyc task are finished */
        protected void onPostExecute(Object o){
            if (server_response == 2) {
                photo_file.delete();
                akt_photo.setImageBitmap(photo_bitmap);
                Toast.makeText(getApplicationContext(), "Hochladen erfolgreich", Toast.LENGTH_LONG).show();
            }else{
                Toast.makeText(getApplicationContext(), "Hochladen fehlgeschlagen", Toast.LENGTH_LONG).show();
            }
            uploadDialog.dismiss();
            super.onPostExecute(o);
        }

    }

    public String getTextFromInputStream(InputStream is){
        BufferedReader reader = new BufferedReader(new InputStreamReader(is));
        StringBuilder stringBuilder = new StringBuilder();
        String aktuelleZeile;
        try {
            while ((aktuelleZeile = reader.readLine()) != null){
                stringBuilder.append(aktuelleZeile);
                stringBuilder.append("\n");
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        return stringBuilder.toString().trim();
    }

    private boolean internetAvailable(){
        ConnectivityManager connectivityManager = (ConnectivityManager) getSystemService(CONNECTIVITY_SERVICE);
        NetworkInfo networkInfo = connectivityManager.getActiveNetworkInfo();
        return networkInfo != null && networkInfo.isConnected();
    }
}
