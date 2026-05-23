## Component Level

### Cloud Sync Component

**Audio.com Service** (project upload/syncing)

- `au3audiocomservice.h/cpp`: contains methods such as:
  - `removeProjectFromDatabase`, so it must interact with the database.
  - `uploadProject`, so it also takes care of uploading projects to `audio.com`...
  - `resumeProjectSync`, `syncingInProgressChanged`, `stopProjectSync` ... and syncing.

**Cloud Service** (user account registration and so on)

- `au3cloudservice.cpp/h`: contains the logic for signing int/out, having methods like
  - `registerWithPassword`
  - `signInWithPassword`
  - `signInWithSocial`
  - `signOut`

**Download Manager** (dedicated module used to download Audacity projects files from the cloud)

- `downloadmanager.h/cpp`: has `startDownload` function, which includes the following lines:

  ```cpp
  const muse::ByteArray data = muse::ByteArray::fromQByteArray(buffer->data());
  const muse::Ret writeRet = filesystem()->writeFile(destPath, data);
  ```

  meaning that it interacts with the File System to save the file as an `.aup3` project file.

  It also has a `scheduleDownloads`, that processes the Download Requests received as an argument (`const std::vector<DownloadRequest>& requests`).
