import { apiCallPost } from "./ApiCalls";

let pageEnterTime: number | null = null;

export function trackPageView(page: string) {
  pageEnterTime = Date.now();
  apiCallPost("/api/auth/activity/", {
    activity_type: "page_view",
    page,
    timestamp: new Date().toISOString(),
  }, true);
}

export function trackPageLeave(page: string) {
  if (pageEnterTime) {
    const duration = (Date.now() - pageEnterTime) / 1000;
    apiCallPost("/api/auth/activity/", {
      activity_type: "page_leave",
      page,
      duration,
      timestamp: new Date().toISOString(),
    }, true);
    pageEnterTime = null;
  }
}

export function trackSearch(page: string, query: string) {
  apiCallPost("/api/auth/activity/", {
    activity_type: "search",
    search_query: query,
    page,
    timestamp: new Date().toISOString(),
  }, true);
}

export function trackFormEdit(formId: number, content: string) {
  apiCallPost("/api/auth/activity/", {
    activity_type: "form_edit",
    form_id: formId,
    form_word_count: content.split(/\s+/).length,
    page: "Form",
    timestamp: new Date().toISOString(),
  }, true);
}

export function trackFormView(formId: number) {
  apiCallPost("/api/auth/activity/", {
    activity_type: "form_view",
    form_id: formId,
    page: "Form",
    timestamp: new Date().toISOString(),
  }, true);
}